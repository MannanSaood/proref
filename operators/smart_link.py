"""
Professional Referencing & Rig UI - Smart Link Operator
Handles intelligent character linking with automatic override setup
Supports: .blend, FBX, USD, Alembic, glTF, OBJ, and more
"""

import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, EnumProperty

from ..core.library_utils import LibraryUtils
from ..core.script_injector import RigUIScriptInjector


# Supported file formats
SUPPORTED_FORMATS = {
    '.blend': 'BLENDER',
    '.fbx': 'FBX',
    '.usd': 'USD',
    '.usda': 'USD',
    '.usdc': 'USD',
    '.usdz': 'USD',
    '.abc': 'ALEMBIC',
    '.gltf': 'GLTF',
    '.glb': 'GLTF',
    '.obj': 'OBJ',
    '.dae': 'COLLADA',
    '.ply': 'PLY',
    '.stl': 'STL',
}

# Formats that are NOT supported but commonly requested (with helpful messages)
UNSUPPORTED_FORMATS = {
    '.ma': "Maya ASCII files cannot be imported directly into Blender. Please export from Maya as FBX or USD first.",
    '.mb': "Maya Binary files cannot be imported directly into Blender. Please export from Maya as FBX or USD first.",
    '.max': "3ds Max files cannot be imported directly. Please export as FBX, OBJ, or USD first.",
    '.c4d': "Cinema 4D files cannot be imported directly. Please export as FBX, Alembic, or USD first.",
    '.hip': "Houdini files cannot be imported directly. Please export as Alembic or USD first.",
    '.zpr': "ZBrush files cannot be imported directly. Please export as OBJ or FBX first.",
    '.blend1': "This is a Blender backup file. Use the original .blend file instead.",
}

# File filter for file browser
FILE_FILTER = ";".join([f"*{ext}" for ext in SUPPORTED_FORMATS.keys()])


class PROREF_OT_SmartLink(Operator):
    """Smart link character with automatic override setup"""
    bl_idname = "proref.smart_link"
    bl_label = "Smart Link Character"
    bl_description = "Link/Import a character with automatic setup. Supports Blend, FBX, USD, Alembic, glTF, and more"
    bl_options = {'REGISTER', 'UNDO'}
    
    # File browser filter
    filter_glob: StringProperty(
        default="*.blend;*.fbx;*.usd;*.usda;*.usdc;*.usdz;*.abc;*.gltf;*.glb;*.obj;*.dae;*.ply;*.stl",
        options={'HIDDEN'}
    )
    
    filepath: StringProperty(
        name="File Path",
        subtype='FILE_PATH'
    )
    
    collection_name: StringProperty(
        name="Collection to Link",
        description="Name of the collection to link (for .blend files only, leave empty to auto-detect)"
    )
    
    # Import options
    import_as_collection: BoolProperty(
        name="Import as Collection",
        description="Group imported objects in a new collection",
        default=True
    )
    
    apply_transforms: BoolProperty(
        name="Apply Transforms",
        description="Apply object transforms on import",
        default=False
    )
    
    def execute(self, context):
        settings = context.scene.proref_settings
        
        if not self.filepath:
            self.report({'ERROR'}, "No file selected")
            return {'CANCELLED'}
        
        # Determine file format
        file_ext = os.path.splitext(self.filepath)[1].lower()
        format_type = SUPPORTED_FORMATS.get(file_ext)
        
        # Check for unsupported but commonly requested formats
        if file_ext in UNSUPPORTED_FORMATS:
            self.report({'ERROR'}, UNSUPPORTED_FORMATS[file_ext])
            return {'CANCELLED'}
        
        if not format_type:
            self.report({'ERROR'}, f"Unsupported file format: {file_ext}. Supported: .blend, .fbx, .usd, .abc, .gltf, .glb, .obj, .dae")
            return {'CANCELLED'}
        
        try:
            # Route to appropriate handler
            if format_type == 'BLENDER':
                return self._handle_blend_file(context, settings)
            else:
                return self._handle_imported_file(context, settings, format_type, file_ext)
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to link/import: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
    
    def _handle_blend_file(self, context, settings):
        """Handle .blend files with library linking"""
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
    
    def _handle_imported_file(self, context, settings, format_type, file_ext):
        """Handle non-blend files with import"""
        # Store current objects to find newly imported ones
        pre_import_objects = set(bpy.data.objects)
        pre_import_armatures = set(bpy.data.armatures)
        
        # Import based on format
        success = self._import_file(format_type)
        
        if not success:
            self.report({'ERROR'}, f"Import failed for {format_type}")
            return {'CANCELLED'}
        
        # Find newly imported objects
        new_objects = [obj for obj in bpy.data.objects if obj not in pre_import_objects]
        
        if not new_objects:
            self.report({'WARNING'}, "No objects were imported")
            return {'CANCELLED'}
        
        # Group into collection if requested
        if self.import_as_collection:
            collection_name = os.path.splitext(os.path.basename(self.filepath))[0]
            new_collection = bpy.data.collections.new(collection_name)
            context.scene.collection.children.link(new_collection)
            
            for obj in new_objects:
                # Unlink from current collections
                for coll in obj.users_collection:
                    coll.objects.unlink(obj)
                # Link to new collection
                new_collection.objects.link(obj)
            
            print(f"Grouped {len(new_objects)} objects into collection '{collection_name}'")
        
        # Find armature (if any)
        armature = None
        for obj in new_objects:
            if obj.type == 'ARMATURE':
                armature = obj
                break
        
        # Select imported objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in new_objects:
            obj.select_set(True)
        
        # Set active object
        if armature:
            context.view_layer.objects.active = armature
        elif new_objects:
            context.view_layer.objects.active = new_objects[0]
        
        self.report({'INFO'}, f"Imported {len(new_objects)} objects from {format_type} file")
        return {'FINISHED'}
    
    def _import_file(self, format_type):
        """Import file based on format type"""
        try:
            if format_type == 'FBX':
                bpy.ops.import_scene.fbx(
                    filepath=self.filepath,
                    use_anim=True,
                    use_custom_props=True,
                    automatic_bone_orientation=True
                )
            
            elif format_type == 'USD':
                bpy.ops.wm.usd_import(
                    filepath=self.filepath,
                    import_guide=True,
                    import_proxy=True,
                    import_render=True,
                    import_visible_only=False
                )
            
            elif format_type == 'ALEMBIC':
                bpy.ops.wm.alembic_import(
                    filepath=self.filepath,
                    as_background_job=False
                )
            
            elif format_type == 'GLTF':
                bpy.ops.import_scene.gltf(
                    filepath=self.filepath
                )
            
            elif format_type == 'OBJ':
                # Blender 4.0+ uses new OBJ importer
                if bpy.app.version >= (4, 0, 0):
                    bpy.ops.wm.obj_import(filepath=self.filepath)
                else:
                    bpy.ops.import_scene.obj(filepath=self.filepath)
            
            elif format_type == 'COLLADA':
                bpy.ops.wm.collada_import(filepath=self.filepath)
            
            elif format_type == 'PLY':
                if bpy.app.version >= (4, 0, 0):
                    bpy.ops.wm.ply_import(filepath=self.filepath)
                else:
                    bpy.ops.import_mesh.ply(filepath=self.filepath)
            
            elif format_type == 'STL':
                if bpy.app.version >= (4, 0, 0):
                    bpy.ops.wm.stl_import(filepath=self.filepath)
                else:
                    bpy.ops.import_mesh.stl(filepath=self.filepath)
            
            else:
                return False
            
            return True
            
        except Exception as e:
            print(f"Import error for {format_type}: {e}")
            return False
    
    def _link_collection(self):
        """Link collection from external .blend file"""
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
        
        script = bpy.data.texts.get(script_name)
        if not script:
            print(f"Auto-execute: Script '{script_name}' not found")
            return False
        
        # Execute the script
        success, error = RigUIScriptInjector.execute_isolated_script(armature, script)
        
        if success:
            print(f"Auto-execute: Successfully ran {script_name}")
        else:
            print(f"Auto-execute: Failed - {error}")
        
        return success
    
    def _select_override(self, context, override_obj):
        """Select the newly created override"""
        bpy.ops.object.select_all(action='DESELECT')
        override_obj.select_set(True)
        context.view_layer.objects.active = override_obj
    
    def invoke(self, context, event):
        """Open file browser with format filter"""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        """Draw import options in file browser"""
        layout = self.layout
        layout.use_property_split = True
        
        box = layout.box()
        box.label(text="Import Options:", icon='IMPORT')
        box.prop(self, "import_as_collection")
        box.prop(self, "apply_transforms")
        
        # Show collection name only for .blend files
        if self.filepath.lower().endswith('.blend'):
            box.prop(self, "collection_name")


class PROREF_OT_BatchLink(Operator):
    """Link multiple characters at once"""
    bl_idname = "proref.batch_link"
    bl_label = "Batch Link Characters"
    bl_description = "Link multiple collections from the same file"
    bl_options = {'REGISTER', 'UNDO'}
    
    filter_glob: StringProperty(
        default="*.blend;*.fbx;*.usd;*.usda;*.usdc;*.usdz;*.abc;*.gltf;*.glb",
        options={'HIDDEN'}
    )
    
    filepath: StringProperty(
        name="File Path",
        subtype='FILE_PATH'
    )
    
    def execute(self, context):
        if not self.filepath:
            self.report({'ERROR'}, "No file selected")
            return {'CANCELLED'}
        
        file_ext = os.path.splitext(self.filepath)[1].lower()
        
        # For .blend files: link all collections
        if file_ext == '.blend':
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
        else:
            # For other formats: just import
            bpy.ops.proref.smart_link(filepath=self.filepath)
            return {'FINISHED'}
    
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
