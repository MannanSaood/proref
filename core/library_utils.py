"""
Professional Referencing & Rig UI - Library Utilities
Low-level functions for working with Blender's library system
"""

import bpy
import os

class LibraryUtils:
    """Utilities for working with linked libraries and overrides"""
    
    @staticmethod
    def get_unique_name(base_name, existing_names=None):
        """
        Generate a unique name for an object
        
        Args:
            base_name: Base name to start from
            existing_names: Set of existing names (optional, uses bpy.data.objects if None)
            
        Returns:
            str: Unique name
        """
        if existing_names is None:
            existing_names = {obj.name for obj in bpy.data.objects}
        
        name = base_name
        counter = 1
        
        while name in existing_names:
            name = f"{base_name}.{counter:03d}"
            counter += 1
        
        return name
    
    @staticmethod
    def make_property_editable(obj, rna_path):
        """
        Make a specific property editable in a library override
        
        Args:
            obj: Object with override
            rna_path: RNA path to the property
            
        Returns:
            bool: Success
        """
        if not obj.override_library:
            return False
        
        try:
            obj.override_library.properties.add(rna_path=rna_path)
            return True
        except Exception as e:
            print(f"Failed to make property editable: {rna_path}, Error: {e}")
            return False
    
    @staticmethod
    def make_all_properties_editable(obj):
        """
        Recursively make all properties editable for an override object
        
        Args:
            obj: Root object with override
            
        Returns:
            int: Number of properties made editable
        """
        count = 0
        
        def process_object(o):
            nonlocal count
            
            if not o.override_library:
                return
            
            # Make object properties editable
            for prop in o.bl_rna.properties:
                if not prop.is_readonly and prop.identifier not in ['rna_type', 'name']:
                    try:
                        o.override_library.properties.add(rna_path=prop.identifier)
                        count += 1
                    except:
                        pass
            
            # Handle armature posebones
            if o.type == 'ARMATURE' and o.pose:
                for bone in o.pose.bones:
                    # Make bone transforms editable
                    for prop_name in ['location', 'rotation_euler', 'rotation_quaternion', 
                                     'rotation_axis_angle', 'scale']:
                        try:
                            rna_path = f'pose.bones["{bone.name}"].{prop_name}'
                            o.override_library.properties.add(rna_path=rna_path)
                            count += 1
                        except:
                            pass
                    
                    # Make bone constraints editable
                    for i, constraint in enumerate(bone.constraints):
                        try:
                            rna_path = f'pose.bones["{bone.name}"].constraints[{i}].influence'
                            o.override_library.properties.add(rna_path=rna_path)
                            count += 1
                        except:
                            pass
            
            # Recurse to children
            for child in o.children:
                process_object(child)
        
        process_object(obj)
        return count
    
    @staticmethod
    def find_armature_in_hierarchy(obj):
        """
        Find the first armature in an object's hierarchy
        
        Args:
            obj: Root object to search from
            
        Returns:
            bpy.types.Object or None: Armature object if found
        """
        if obj.type == 'ARMATURE':
            return obj
        
        for child in obj.children_recursive:
            if child.type == 'ARMATURE':
                return child
        
        return None
    
    @staticmethod
    def get_library_info(library):
        """
        Get detailed information about a library
        
        Args:
            library: bpy.types.Library
            
        Returns:
            dict: Library information
        """
        filepath_abs = bpy.path.abspath(library.filepath)
        
        return {
            'name': library.name,
            'filepath': library.filepath,
            'filepath_abs': filepath_abs,
            'exists': os.path.exists(filepath_abs),
            'parent': library.parent.name if library.parent else None,
        }
    
    @staticmethod
    def find_all_libraries():
        """
        Find all linked libraries in the current file
        
        Returns:
            list: List of bpy.types.Library objects
        """
        return [lib for lib in bpy.data.libraries]
    
    @staticmethod
    def find_overrides_for_library(library):
        """
        Find all override objects that reference a specific library
        
        Args:
            library: bpy.types.Library
            
        Returns:
            list: List of override objects
        """
        overrides = []
        
        for obj in bpy.data.objects:
            if obj.override_library and obj.override_library.reference:
                if obj.override_library.reference.library == library:
                    overrides.append(obj)
        
        return overrides
    
    @staticmethod
    def relocate_library(library, new_path):
        """
        Relocate a library to a new file path
        
        Args:
            library: bpy.types.Library
            new_path: New file path
            
        Returns:
            bool: Success
        """
        try:
            library.filepath = new_path
            library.reload()
            return True
        except Exception as e:
            print(f"Failed to relocate library: {e}")
            return False
    
    @staticmethod
    def reload_library(library):
        """
        Reload a library from disk
        
        Args:
            library: bpy.types.Library
            
        Returns:
            bool: Success
        """
        try:
            library.reload()
            return True
        except Exception as e:
            print(f"Failed to reload library: {e}")
            return False
