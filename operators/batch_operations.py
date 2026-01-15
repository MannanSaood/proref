"""
Professional Referencing & Rig UI - Batch Operations
Batch relink, version bumping, and folder search operations
"""

import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

from ..core.library_utils import LibraryUtils
from ..core.version_utils import VersionUtils

class PROREF_OT_BatchRelink(Operator):
    """Batch relink multiple libraries using find/replace"""
    bl_idname = "proref.batch_relink"
    bl_label = "Batch Relink Libraries"
    bl_description = "Update file paths for multiple libraries at once using find and replace"
    bl_options = {'REGISTER', 'UNDO'}
    
    search_string: StringProperty(
        name="Search For",
        description="Text to search for in file paths (e.g., 'S:\\')",
        default=""
    )
    
    replace_string: StringProperty(
        name="Replace With",
        description="Text to replace with (e.g., 'P:\\')",
        default=""
    )
    
    def execute(self, context):
        settings = context.scene.proref_settings
        
        if not self.search_string:
            self.report({'ERROR'}, "Search string cannot be empty")
            return {'CANCELLED'}
        
        # Get selected libraries
        selected_libs = [lib for lib in settings.linked_libraries if lib.selected]
        
        if not selected_libs:
            self.report({'ERROR'}, "No libraries selected. Use checkboxes in Reference Manager")
            return {'CANCELLED'}
        
        success_count = 0
        failed_count = 0
        
        for lib_data in selected_libs:
            library = bpy.data.libraries.get(lib_data.library_name)
            
            if not library:
                failed_count += 1
                continue
            
            old_path = library.filepath
            
            # Check if search string is in path
            if self.search_string not in old_path:
                print(f"Skipping {lib_data.library_name}: search string not found in path")
                continue
            
            # Perform replacement
            new_path = old_path.replace(self.search_string, self.replace_string)
            
            # Attempt relocation
            if LibraryUtils.relocate_library(library, new_path):
                success_count += 1
                print(f"Relinked: {lib_data.library_name} -> {new_path}")
            else:
                failed_count += 1
                print(f"Failed to relink: {lib_data.library_name}")
        
        # Update library list
        bpy.ops.proref.update_library_list()
        
        msg = f"Relinked {success_count} libraries"
        if failed_count > 0:
            msg += f" ({failed_count} failed)"
        
        self.report({'INFO'}, msg)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.label(text="Find and Replace in Library Paths:")
        col.prop(self, "search_string")
        col.prop(self, "replace_string")
        
        col.separator()
        
        settings = context.scene.proref_settings
        selected_count = sum(1 for lib in settings.linked_libraries if lib.selected)
        col.label(text=f"Will update {selected_count} selected libraries", icon='INFO')


class PROREF_OT_BatchSearchFolder(Operator):
    """Search a folder for missing library files"""
    bl_idname = "proref.batch_search_folder"
    bl_label = "Search Folder for Libraries"
    bl_description = "Search a folder for missing library files by filename"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory: StringProperty(
        name="Search Directory",
        subtype='DIR_PATH'
    )
    
    recursive: BoolProperty(
        name="Recursive Search",
        description="Search subdirectories as well",
        default=True
    )
    
    def execute(self, context):
        settings = context.scene.proref_settings
        
        if not self.directory or not os.path.exists(self.directory):
            self.report({'ERROR'}, "Invalid directory")
            return {'CANCELLED'}
        
        # Get selected libraries
        selected_libs = [lib for lib in settings.linked_libraries if lib.selected]
        
        if not selected_libs:
            self.report({'ERROR'}, "No libraries selected")
            return {'CANCELLED'}
        
        success_count = 0
        
        for lib_data in selected_libs:
            library = bpy.data.libraries.get(lib_data.library_name)
            
            if not library:
                continue
            
            # Get filename
            filename = os.path.basename(library.filepath)
            
            # Search for file
            found_path = self._find_file(self.directory, filename, self.recursive)
            
            if found_path:
                if LibraryUtils.relocate_library(library, found_path):
                    success_count += 1
                    print(f"Found and relinked: {filename} -> {found_path}")
        
        # Update library list
        bpy.ops.proref.update_library_list()
        
        self.report({'INFO'}, f"Found and relinked {success_count} libraries")
        return {'FINISHED'}
    
    def _find_file(self, directory, filename, recursive):
        """Search for a file in directory"""
        from pathlib import Path
        
        search_path = Path(directory)
        
        if recursive:
            # Recursive search
            for file_path in search_path.rglob(filename):
                if file_path.is_file():
                    return str(file_path)
        else:
            # Non-recursive search
            for file_path in search_path.glob(filename):
                if file_path.is_file():
                    return str(file_path)
        
        return None
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class PROREF_OT_DetectVersions(Operator):
    """Detect version numbers for selected libraries"""
    bl_idname = "proref.detect_versions"
    bl_label = "Detect Versions"
    bl_description = "Scan for version numbers and check for newer versions"
    
    def execute(self, context):
        settings = context.scene.proref_settings
        
        detected_count = 0
        newer_available = 0
        
        for lib_data in settings.linked_libraries:
            library = bpy.data.libraries.get(lib_data.library_name)
            
            if not library:
                continue
            
            # Get version info
            version_info = VersionUtils.get_version_info(library.filepath)
            
            if version_info['current_version'] is not None:
                lib_data.version_number = version_info['current_version']
                detected_count += 1
                
                if version_info['has_newer']:
                    lib_data.has_newer_version = True
                    newer_available += 1
                    print(f"{lib_data.library_name}: v{version_info['current_version']:02d} "
                          f"(v{version_info['latest_version']:02d} available)")
                else:
                    lib_data.has_newer_version = False
            else:
                lib_data.version_number = 0
                lib_data.has_newer_version = False
        
        msg = f"Detected versions for {detected_count} libraries"
        if newer_available > 0:
            msg += f" ({newer_available} have updates)"
        
        self.report({'INFO'}, msg)
        return {'FINISHED'}


class PROREF_OT_BumpToLatest(Operator):
    """Upgrade selected libraries to their latest version"""
    bl_idname = "proref.bump_to_latest"
    bl_label = "Bump to Latest Version"
    bl_description = "Update selected libraries to the latest version found on disk"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.proref_settings
        
        # Get selected libraries with newer versions available
        selected_libs = [lib for lib in settings.linked_libraries 
                        if lib.selected and lib.has_newer_version]
        
        if not selected_libs:
            self.report({'WARNING'}, "No selected libraries have newer versions")
            return {'CANCELLED'}
        
        success_count = 0
        
        for lib_data in selected_libs:
            library = bpy.data.libraries.get(lib_data.library_name)
            
            if not library:
                continue
            
            # Get latest version path
            latest_path, latest_version = VersionUtils.get_latest_version(library.filepath)
            
            if latest_path and latest_path != library.filepath:
                if LibraryUtils.relocate_library(library, latest_path):
                    success_count += 1
                    print(f"Upgraded {lib_data.library_name}: "
                          f"v{lib_data.version_number:02d} -> v{latest_version:02d}")
                    
                    # Update stored version
                    lib_data.version_number = latest_version
                    lib_data.has_newer_version = False
        
        self.report({'INFO'}, f"Upgraded {success_count} libraries to latest version")
        return {'FINISHED'}


class PROREF_OT_SelectAllLibraries(Operator):
    """Select or deselect all libraries"""
    bl_idname = "proref.select_all_libraries"
    bl_label = "Select All"
    bl_description = "Select or deselect all libraries"
    
    action: StringProperty(default='SELECT')  # SELECT, DESELECT, TOGGLE
    
    def execute(self, context):
        settings = context.scene.proref_settings
        
        if self.action == 'SELECT':
            for lib in settings.linked_libraries:
                lib.selected = True
        elif self.action == 'DESELECT':
            for lib in settings.linked_libraries:
                lib.selected = False
        elif self.action == 'TOGGLE':
            for lib in settings.linked_libraries:
                lib.selected = not lib.selected
        
        return {'FINISHED'}


class PROREF_OT_SelectByPattern(Operator):
    """Select libraries matching a pattern"""
    bl_idname = "proref.select_by_pattern"
    bl_label = "Select by Pattern"
    bl_description = "Select libraries whose names match a pattern"
    
    pattern: StringProperty(
        name="Pattern",
        description="Text pattern to match (case-insensitive)",
        default=""
    )
    
    def execute(self, context):
        settings = context.scene.proref_settings
        
        if not self.pattern:
            return {'CANCELLED'}
        
        match_count = 0
        pattern_lower = self.pattern.lower()
        
        for lib in settings.linked_libraries:
            if pattern_lower in lib.library_name.lower():
                lib.selected = True
                match_count += 1
        
        self.report({'INFO'}, f"Selected {match_count} matching libraries")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class PROREF_OT_BatchReloadLibraries(Operator):
    """Reload all selected libraries from disk"""
    bl_idname = "proref.batch_reload_libraries"
    bl_label = "Batch Reload Libraries"
    bl_description = "Reload all selected libraries from disk"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        settings = context.scene.proref_settings
        
        # Get selected libraries
        selected_libs = [lib for lib in settings.linked_libraries if lib.selected]
        
        if not selected_libs:
            self.report({'ERROR'}, "No libraries selected")
            return {'CANCELLED'}
        
        success_count = 0
        failed_count = 0
        
        for lib_data in selected_libs:
            library = bpy.data.libraries.get(lib_data.library_name)
            
            if not library:
                failed_count += 1
                continue
            
            try:
                library.reload()
                success_count += 1
                print(f"Reloaded: {lib_data.library_name}")
            except Exception as e:
                failed_count += 1
                print(f"Failed to reload {lib_data.library_name}: {e}")
        
        # Update library list
        bpy.ops.proref.update_library_list()
        
        msg = f"Reloaded {success_count} libraries"
        if failed_count > 0:
            msg += f" ({failed_count} failed)"
        
        self.report({'INFO'}, msg)
        return {'FINISHED'}


# Registration
classes = (
    PROREF_OT_BatchRelink,
    PROREF_OT_BatchSearchFolder,
    PROREF_OT_DetectVersions,
    PROREF_OT_BumpToLatest,
    PROREF_OT_SelectAllLibraries,
    PROREF_OT_SelectByPattern,
    PROREF_OT_BatchReloadLibraries,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)