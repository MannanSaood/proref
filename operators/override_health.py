"""
Professional Referencing & Rig UI - Override Health Operators
Health checking and repair operations for library overrides
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

from ..core.validation import OverrideValidator
from ..core.library_utils import LibraryUtils

class PROREF_OT_HealthCheck(Operator):
    """Run comprehensive health check on all library overrides"""
    bl_idname = "proref.health_check"
    bl_label = "Run Health Check"
    bl_description = "Check all library overrides for issues and update health status"
    
    def execute(self, context):
        settings = context.scene.proref_settings
        settings.health_checks.clear()
        
        overrides = OverrideValidator.find_all_overrides_in_scene()
        
        if not overrides:
            self.report({'INFO'}, "No library overrides found in scene")
            return {'FINISHED'}
        
        healthy_count = 0
        warning_count = 0
        error_count = 0
        
        for obj in overrides:
            health_data = OverrideValidator.check_override_health(obj)
            
            # Add to health checks list
            item = settings.health_checks.add()
            item.object_name = obj.name
            
            # Get armature name if applicable
            armature = LibraryUtils.find_armature_in_hierarchy(obj)
            if armature:
                item.armature_name = armature.name
            else:
                item.armature_name = obj.name
            
            # Set health status
            if health_data['is_healthy']:
                if health_data['warnings']:
                    item.health_status = 'WARNING'
                    warning_count += 1
                else:
                    item.health_status = 'HEALTHY'
                    healthy_count += 1
            else:
                item.health_status = 'ERROR'
                error_count += 1
            
            # Set issue data
            item.issue_count = len(health_data['issues'])
            all_issues = health_data['issues'] + health_data['warnings']
            item.issue_description = "; ".join(all_issues[:3])  # First 3 issues
            
            # Set metadata
            if 'locked_bone_count' in health_data['info']:
                item.locked_bone_count = health_data['info']['locked_bone_count']
            
            item.has_rig_ui = health_data['info'].get('has_rig_ui', False)
            
            if 'library_path' in health_data['info']:
                item.library_path = health_data['info']['library_path']
        
        # Report summary
        total = len(overrides)
        msg = f"Health check complete: {healthy_count} healthy, {warning_count} warnings, {error_count} errors"
        self.report({'INFO'}, msg)
        
        return {'FINISHED'}


class PROREF_OT_RepairOverride(Operator):
    """One-click repair for common override issues"""
    bl_idname = "proref.repair_override"
    bl_label = "Repair Override"
    bl_description = "Automatically fix common override issues"
    bl_options = {'REGISTER', 'UNDO'}
    
    object_name: StringProperty(
        name="Object Name",
        description="Name of the object to repair"
    )
    
    def execute(self, context):
        obj = bpy.data.objects.get(self.object_name) if self.object_name else context.active_object
        
        if not obj:
            self.report({'ERROR'}, "No object to repair")
            return {'CANCELLED'}
        
        if not obj.override_library:
            self.report({'ERROR'}, f"{obj.name} is not a library override")
            return {'CANCELLED'}
        
        # Collect all repairs made
        repairs = []
        errors = []
        
        # Run diagnostics
        issues = OverrideValidator.diagnose_common_issues(obj)
        
        for issue_type, description, severity in issues:
            result = self._attempt_repair(obj, issue_type, context)
            if result['success']:
                repairs.append(result['message'])
            elif result['error']:
                errors.append(result['error'])
        
        # Additional repairs not based on diagnostics
        
        # Repair 1: Ensure properties are editable
        if not any('editable' in r.lower() for r in repairs):
            count = LibraryUtils.make_all_properties_editable(obj)
            if count > 0:
                repairs.append(f"Made {count} properties editable")
        
        # Repair 2: Fix armature-specific issues
        if obj.type == 'ARMATURE':
            armature_repairs = self._repair_armature(obj)
            repairs.extend(armature_repairs)
        
        # Repair 3: Fix rig UI reference
        rig_ui_repair = self._repair_rig_ui_reference(obj)
        if rig_ui_repair:
            repairs.append(rig_ui_repair)
        
        # Report results
        if repairs:
            self.report({'INFO'}, f"Repairs made: {', '.join(repairs)}")
            return {'FINISHED'}
        elif errors:
            self.report({'WARNING'}, f"Could not repair: {', '.join(errors)}")
            return {'CANCELLED'}
        else:
            self.report({'INFO'}, "No repairs needed - override is healthy")
            return {'FINISHED'}
    
    def _attempt_repair(self, obj, issue_type, context):
        """Attempt to repair a specific issue type"""
        result = {'success': False, 'message': '', 'error': None}
        
        if issue_type == 'NO_EDITABLE_PROPS':
            count = LibraryUtils.make_all_properties_editable(obj)
            if count > 0:
                result['success'] = True
                result['message'] = f"Made {count} properties editable"
        
        elif issue_type == 'MISSING_REFERENCE':
            result['error'] = "Cannot auto-repair missing reference"
        
        elif issue_type == 'LIBRARY_NOT_FOUND':
            result['error'] = "Library file missing - use Relocate"
        
        elif issue_type == 'SYSTEM_OVERRIDE':
            # Try to convert system override to editable
            try:
                if hasattr(obj.override_library, 'is_system_override'):
                    obj.override_library.is_system_override = False
                    result['success'] = True
                    result['message'] = "Converted system override to editable"
            except Exception as e:
                result['error'] = f"Could not convert system override: {e}"
        
        return result
    
    def _repair_armature(self, armature):
        """Repair armature-specific issues"""
        repairs = []
        
        if not armature.pose:
            return repairs
        
        # Unlock bones that are fully locked
        unlocked = 0
        for bone in armature.pose.bones:
            was_locked = False
            
            # Only unlock if ALL transforms are locked (likely unintentional)
            if all(bone.lock_location) and all(bone.lock_rotation) and all(bone.lock_scale):
                bone.lock_location = (False, False, False)
                bone.lock_rotation = (False, False, False)
                bone.lock_scale = (False, False, False)
                unlocked += 1
        
        if unlocked > 0:
            repairs.append(f"Unlocked {unlocked} fully-locked bones")
        
        return repairs
    
    def _repair_rig_ui_reference(self, obj):
        """Repair rig UI script reference"""
        armature = obj if obj.type == 'ARMATURE' else LibraryUtils.find_armature_in_hierarchy(obj)
        
        if not armature:
            return None
        
        # Check if rig UI reference is broken
        script_name = armature.get("proref_rig_ui")
        if script_name and script_name not in bpy.data.texts:
            # Try to find original script
            original_name = armature.get("proref_original_script")
            if original_name and original_name in bpy.data.texts:
                armature["proref_rig_ui"] = original_name
                return f"Restored rig UI reference to {original_name}"
            else:
                # Clear broken reference
                del armature["proref_rig_ui"]
                return "Cleared broken rig UI reference"
        
        return None


class PROREF_OT_ResyncOverride(Operator):
    """Targeted resync - only resyncs selected override, not full hierarchy"""
    bl_idname = "proref.resync_override"
    bl_label = "Resync Override"
    bl_description = "Resync only this override (preserves other characters' changes)"
    bl_options = {'REGISTER', 'UNDO'}
    
    object_name: StringProperty(name="Object Name")
    
    resync_mode: bpy.props.EnumProperty(
        name="Resync Mode",
        items=[
            ('SINGLE', "Single Object", "Resync only this object"),
            ('HIERARCHY', "With Children", "Resync this object and its children"),
        ],
        default='SINGLE'
    )
    
    def execute(self, context):
        obj = bpy.data.objects.get(self.object_name) if self.object_name else context.active_object
        
        if not obj or not obj.override_library:
            self.report({'ERROR'}, "Not a library override")
            return {'CANCELLED'}
        
        try:
            # Store current state for potential recovery
            stored_transforms = self._store_bone_transforms(obj)
            
            # Store current selection
            original_active = context.view_layer.objects.active
            original_selection = [o for o in context.selected_objects]
            
            # Select only the target override
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            
            # Perform targeted resync based on mode
            if self.resync_mode == 'SINGLE':
                # Use single object resync (Blender 3.2+)
                try:
                    bpy.ops.object.lib_override_resync_clear_single()
                    self.report({'INFO'}, f"Resynced {obj.name} (single)")
                except AttributeError:
                    # Fallback for older Blender versions
                    obj.override_library.resync(context.blend_data, context.scene, "APPLY")
                    self.report({'INFO'}, f"Resynced {obj.name}")
            else:
                # Hierarchy resync - but only for this character's hierarchy
                bpy.ops.outliner.liboverride_operation(
                    type='OVERRIDE_LIBRARY_RESYNC_HIERARCHY'
                )
                self.report({'INFO'}, f"Resynced {obj.name} hierarchy")
            
            # Restore selection
            bpy.ops.object.select_all(action='DESELECT')
            for o in original_selection:
                if o.name in bpy.data.objects:
                    o.select_set(True)
            context.view_layer.objects.active = original_active
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Resync failed: {str(e)}")
            return {'CANCELLED'}
    
    def _store_bone_transforms(self, obj):
        """Store bone transforms for recovery if needed"""
        transforms = {}
        
        if obj.type == 'ARMATURE' and obj.pose:
            for bone in obj.pose.bones:
                transforms[bone.name] = {
                    'location': bone.location.copy(),
                    'rotation': bone.rotation_quaternion.copy(),
                    'scale': bone.scale.copy(),
                }
        
        return transforms
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "resync_mode")


class PROREF_OT_MakeEditable(Operator):
    """Make all properties of selected override editable"""
    bl_idname = "proref.make_all_editable"
    bl_label = "Make All Editable"
    bl_description = "Make all properties editable for the selected override"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        
        if not obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        
        if not obj.override_library:
            self.report({'ERROR'}, "Not a library override")
            return {'CANCELLED'}
        
        count = LibraryUtils.make_all_properties_editable(obj)
        
        self.report({'INFO'}, f"Made {count} properties editable")
        return {'FINISHED'}


class PROREF_OT_UpdateLibraryList(Operator):
    """Update the list of linked libraries with detailed info"""
    bl_idname = "proref.update_library_list"
    bl_label = "Update Library List"
    bl_description = "Refresh the list of linked libraries in the scene"
    
    def execute(self, context):
        import os
        from datetime import datetime
        
        settings = context.scene.proref_settings
        settings.linked_libraries.clear()
        
        libraries = LibraryUtils.find_all_libraries()
        
        for lib in libraries:
            item = settings.linked_libraries.add()
            info = LibraryUtils.get_library_info(lib)
            
            item.library_name = info['name']
            item.filepath = info['filepath']
            item.exists = info['exists']
            
            # Count overrides
            overrides = LibraryUtils.find_overrides_for_library(lib)
            item.override_count = len(overrides)
            
            # Get file size and modification date
            if info['exists']:
                abs_path = info.get('filepath_abs', bpy.path.abspath(info['filepath']))
                try:
                    stat = os.stat(abs_path)
                    
                    # Human-readable file size
                    size = stat.st_size
                    if size < 1024:
                        item.file_size = f"{size} B"
                    elif size < 1024 * 1024:
                        item.file_size = f"{size / 1024:.1f} KB"
                    else:
                        item.file_size = f"{size / (1024 * 1024):.1f} MB"
                    
                    # Modification date
                    mtime = datetime.fromtimestamp(stat.st_mtime)
                    item.last_modified = mtime.strftime("%Y-%m-%d %H:%M")
                    
                except Exception as e:
                    item.file_size = "Unknown"
                    item.last_modified = ""
        
        self.report({'INFO'}, f"Found {len(libraries)} linked libraries")
        return {'FINISHED'}



class PROREF_OT_RelocateLibrary(Operator):
    """Relocate a library to a new file path"""
    bl_idname = "proref.relocate_library"
    bl_label = "Relocate Library"
    bl_description = "Change the file path of a linked library"
    bl_options = {'REGISTER', 'UNDO'}
    
    library_name: StringProperty(name="Library Name")
    filepath: StringProperty(name="New Path", subtype='FILE_PATH')
    
    def execute(self, context):
        if not self.library_name:
            self.report({'ERROR'}, "No library specified")
            return {'CANCELLED'}
        
        library = bpy.data.libraries.get(self.library_name)
        if not library:
            self.report({'ERROR'}, f"Library '{self.library_name}' not found")
            return {'CANCELLED'}
        
        if LibraryUtils.relocate_library(library, self.filepath):
            self.report({'INFO'}, f"Relocated {self.library_name}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Relocation failed")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class PROREF_OT_ReloadLibrary(Operator):
    """Reload a single library from disk"""
    bl_idname = "proref.reload_library"
    bl_label = "Reload Library"
    bl_description = "Reload this library file from disk"
    bl_options = {'REGISTER', 'UNDO'}
    
    library_name: StringProperty(name="Library Name")
    
    def execute(self, context):
        if not self.library_name:
            self.report({'ERROR'}, "No library specified")
            return {'CANCELLED'}
        
        library = bpy.data.libraries.get(self.library_name)
        if not library:
            self.report({'ERROR'}, f"Library '{self.library_name}' not found")
            return {'CANCELLED'}
        
        try:
            library.reload()
            self.report({'INFO'}, f"Reloaded {self.library_name}")
            
            # Refresh the library list
            bpy.ops.proref.update_library_list()
            
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Reload failed: {str(e)}")
            return {'CANCELLED'}


class PROREF_OT_SelectAllLibraries(Operator):
    """Select all libraries for batch operations"""
    bl_idname = "proref.select_all_libraries"
    bl_label = "Select All"
    bl_description = "Select all libraries for batch operations"
    
    def execute(self, context):
        settings = context.scene.proref_settings
        for lib in settings.linked_libraries:
            lib.is_selected = True
        return {'FINISHED'}


class PROREF_OT_DeselectAllLibraries(Operator):
    """Deselect all libraries"""
    bl_idname = "proref.deselect_all_libraries"
    bl_label = "Deselect All"
    bl_description = "Deselect all libraries"
    
    def execute(self, context):
        settings = context.scene.proref_settings
        for lib in settings.linked_libraries:
            lib.is_selected = False
        return {'FINISHED'}


class PROREF_OT_BatchReloadLibraries(Operator):
    """Reload all selected libraries"""
    bl_idname = "proref.batch_reload_libraries"
    bl_label = "Batch Reload"
    bl_description = "Reload all selected libraries from disk"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.proref_settings
        
        selected = [lib for lib in settings.linked_libraries if lib.is_selected and lib.exists]
        
        if not selected:
            self.report({'WARNING'}, "No libraries selected (or all missing)")
            return {'CANCELLED'}
        
        success_count = 0
        fail_count = 0
        
        for lib_data in selected:
            library = bpy.data.libraries.get(lib_data.library_name)
            if library:
                try:
                    library.reload()
                    success_count += 1
                except Exception as e:
                    print(f"Failed to reload {lib_data.library_name}: {e}")
                    fail_count += 1
        
        # Refresh the library list
        bpy.ops.proref.update_library_list()
        
        if fail_count > 0:
            self.report({'WARNING'}, f"Reloaded {success_count}, failed {fail_count}")
        else:
            self.report({'INFO'}, f"Reloaded {success_count} libraries")
        
        return {'FINISHED'}


# Registration
classes = (
    PROREF_OT_HealthCheck,
    PROREF_OT_RepairOverride,
    PROREF_OT_ResyncOverride,
    PROREF_OT_MakeEditable,
    PROREF_OT_UpdateLibraryList,
    PROREF_OT_RelocateLibrary,
    PROREF_OT_ReloadLibrary,
    PROREF_OT_SelectAllLibraries,
    PROREF_OT_DeselectAllLibraries,
    PROREF_OT_BatchReloadLibraries,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
