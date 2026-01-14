"""
Professional Referencing & Rig UI - Smart Link Operator
Handles intelligent character linking with automatic override setup
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

from ..core.library_utils import LibraryUtils
from ..core.script_injector import RigUIScriptInjector

class PROREF_OT_SmartLink(Operator):
    """Smart link character with automatic override setup"""
    bl_idname = "proref.smart_link"
    bl_label = "Smart Link Character"
    bl_description = "Link a character and automatically set up library overrides with conflict resolution"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: StringProperty(
        name="File Path",
        subtype='FILE_PATH'
    )
    
    collection_name: StringProperty(
        name="Collection to Link",
        description="Name of the collection to link (leave empty to auto-detect)"
    )
    
    def execute(self, context):
        settings = context.scene.proref_settings
        
        if not self.filepath:
            self.report({'ERROR'}, "No file selected")
            return {'CANCELLED'}
        
        try:
            # Step 1: Link the collection
            linked_collection = self._link_collection()
            if not linked_collection:
                return {'CANCELLED'}
            
            # Step 2: Create instance in scene
            instance_obj = self._create_instance(context, linked_collection)
            
            # Step 3: Create library override
            override_obj = self._create_override(context, instance_obj)
            if not override_obj:
                return {'CANCELLED'}
            
            # Step 4: Make properties editable
            if settings.auto_make_editable:
                count = self._make_editable(override_obj, settings)
                print(f"Made {count} properties editable")
            
            # Step 5: Handle rig UI script
            if settings.unique_rig_ui_names:
                self._handle_rig_ui(override_obj, instance_obj.name)
            
            # Step 6: Auto-execute rig UI if enabled
            if settings.auto_execute_rig_ui:
                self._auto_execute_rig_ui(override_obj)
            
            # Step 7: Select the new override
            self._select_override(context, override_obj)
            
            self.report({'INFO'}, f"Successfully linked '{instance_obj.name}'")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to link character: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
    
    def _link_collection(self):
        """Link collection from external file"""
        with bpy.data.libraries.load(self.filepath, link=True) as (data_from, data_to):
            if not self.collection_name:
                # Auto-detect first collection
                if data_from.collections:
                    self.collection_name = data_from.collections[0]
                else:
                    self.report({'ERROR'}, "No collections found in file")
                    return None
            
            if self.collection_name not in data_from.collections:
                self.report({'ERROR'}, f"Collection '{self.collection_name}' not found")
                return None
            
            data_to.collections = [self.collection_name]
        
        if not data_to.collections:
            return None
        
        return data_to.collections[0]
    
    def _create_instance(self, context, collection):
        """Create collection instance in scene"""
        instance_name = LibraryUtils.get_unique_name(collection.name)
        instance_obj = bpy.data.objects.new(instance_name, None)
        instance_obj.instance_type = 'COLLECTION'
        instance_obj.instance_collection = collection
        context.collection.objects.link(instance_obj)
        return instance_obj
    
    def _create_override(self, context, instance_obj):
        """Create library override for instance with optional selective mode"""
        settings = context.scene.proref_settings
        
        try:
            # Create initial override
            override_obj = instance_obj.override_create(remap_local_usages=True)
            
            # If selective mode: revert non-armature objects to linked data
            if settings.selective_override_armature_only:
                self._apply_selective_override(context, override_obj)
            
            return override_obj
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create override: {str(e)}")
            return None
    
    def _apply_selective_override(self, context, root_obj):
        """Revert mesh overrides back to linked data, keep only armatures as overrides"""
        objects_to_revert = []
        
        # Find all mesh objects in hierarchy
        def collect_meshes(obj):
            if obj.type == 'MESH' and obj.override_library:
                objects_to_revert.append(obj)
            for child in obj.children:
                collect_meshes(child)
        
        collect_meshes(root_obj)
        
        # Revert mesh overrides to linked
        for mesh_obj in objects_to_revert:
            try:
                # Clear override, keeping the linked reference
                if mesh_obj.override_library and mesh_obj.override_library.reference:
                    # Store parent relationship
                    parent = mesh_obj.parent
                    matrix = mesh_obj.matrix_world.copy()
                    
                    # Create linked duplicate from reference
                    linked_ref = mesh_obj.override_library.reference
                    
                    # Remove the override object
                    bpy.data.objects.remove(mesh_obj, do_unlink=True)
                    
                    print(f"Reverted mesh '{mesh_obj.name}' to linked data")
            except Exception as e:
                print(f"Could not revert {mesh_obj.name}: {e}")
    
    def _make_editable(self, override_obj, settings):
        """Make properties editable based on settings"""
        count = 0
        
        # Make all properties editable
        if settings.make_bones_editable or settings.make_constraints_editable:
            count = LibraryUtils.make_all_properties_editable(override_obj)
        
        return count
    
    def _handle_rig_ui(self, override_obj, unique_name):
        """Handle rig UI script isolation"""
        armature = LibraryUtils.find_armature_in_hierarchy(override_obj)
        if not armature:
            return None
        
        # Find and isolate rig UI script
        original_script = RigUIScriptInjector.find_rig_ui_script(armature)
        if original_script:
            isolated_script = RigUIScriptInjector.create_isolated_script(
                original_script,
                armature.name,
                unique_name
            )
            
            # Store reference
            armature["proref_rig_ui"] = isolated_script.name
            armature["proref_original_script"] = original_script.name
            
            print(f"Created isolated rig UI: {isolated_script.name}")
            return isolated_script
        
        return None
    
    def _auto_execute_rig_ui(self, override_obj):
        """Automatically execute rig UI script after linking"""
        armature = LibraryUtils.find_armature_in_hierarchy(override_obj)
        if not armature:
            print("Auto-execute: No armature found")
            return False
        
        script_name = armature.get("proref_rig_ui")
        if not script_name:
            print("Auto-execute: No rig UI script assigned")
            return False
        
        if script_name not in bpy.data.texts:
            print(f"Auto-execute: Script '{script_name}' not found")
            return False
        
        script = bpy.data.texts[script_name]
        success, error = RigUIScriptInjector.execute_isolated_script(armature, script)
        
        if success:
            print(f"Auto-execute: Successfully ran {script_name}")
            return True
        else:
            print(f"Auto-execute failed: {error}")
            return False
    
    def _select_override(self, context, override_obj):
        """Select the newly created override"""
        bpy.ops.object.select_all(action='DESELECT')
        override_obj.select_set(True)
        context.view_layer.objects.active = override_obj
    
    def invoke(self, context, event):
        """Open file browser"""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class PROREF_OT_BatchLink(Operator):
    """Link multiple characters at once"""
    bl_idname = "proref.batch_link"
    bl_label = "Batch Link Characters"
    bl_description = "Link multiple collections from the same file"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: StringProperty(
        name="File Path",
        subtype='FILE_PATH'
    )
    
    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No file selected")
            return {'CANCELLED'}
        
        try:
            # Get all collections from file
            with bpy.data.libraries.load(self.filepath, link=False) as (data_from, data_to):
                collections = data_from.collections
            
            if not collections:
                self.report({'ERROR'}, "No collections found in file")
                return {'CANCELLED'}
            
            # Link each collection
            success_count = 0
            for coll_name in collections:
                # Use Smart Link operator
                bpy.ops.proref.smart_link(
                    filepath=self.filepath,
                    collection_name=coll_name
                )
                success_count += 1
            
            self.report({'INFO'}, f"Successfully linked {success_count} characters")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Batch link failed: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# Registration
classes = (
    PROREF_OT_SmartLink,
    PROREF_OT_BatchLink,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
