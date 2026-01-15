"""
Professional Referencing & Rig UI - Reference Manager Panel
Visual management interface for linked libraries
"""

import bpy
from bpy.types import Panel, UIList


class PROREF_UL_LibraryList(UIList):
    """UI List for displaying linked libraries"""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        settings = context.scene.proref_settings
        
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # v1.5: Selection checkbox
            layout.prop(item, "selected", text="")
            
            # Library status icon
            if item.exists:
                status_icon = 'LINKED'
            else:
                status_icon = 'ERROR'
            
            # Library name
            split = layout.split(factor=0.4)
            split.label(text=item.library_name, icon=status_icon)
            
            # v1.5: Version info or override count
            if settings.show_version_info and item.version_number > 0:
                version_col = split.row()
                version_col.label(text=f"v{item.version_number:02d}")
                
                # Show upgrade indicator
                if item.has_newer_version:
                    version_col.label(text="", icon='TRIA_UP')
            else:
                split.label(text=f"{item.override_count} overrides")
            
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.library_name)


class PROREF_PT_ReferenceManager(Panel):
    """Reference Manager - Visual library overview"""
    bl_label = "Reference Manager"
    bl_idname = "PROREF_PT_reference_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pro Ref"
    bl_parent_id = "PROREF_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.proref_settings
        
        # Update button
        row = layout.row()
        row.scale_y = 1.2
        row.operator("proref.update_library_list", text="Refresh Library List", icon='FILE_REFRESH')
        
        # v1.5: Version detection toggle
        layout.prop(settings, "show_version_info", text="Show Versions")
        
        if not settings.linked_libraries:
            layout.label(text="No linked libraries found", icon='INFO')
            layout.label(text="Link a character to get started")
            return
        
        # v1.5: Selection controls
        box = layout.box()
        box.label(text="Selection:", icon='RESTRICT_SELECT_OFF')
        row = box.row(align=True)
        
        op = row.operator("proref.select_all_libraries", text="All")
        op.action = 'SELECT'
        
        op = row.operator("proref.select_all_libraries", text="None")
        op.action = 'DESELECT'
        
        op = row.operator("proref.select_all_libraries", text="Invert")
        op.action = 'TOGGLE'
        
        row.operator("proref.select_by_pattern", text="", icon='VIEWZOOM')
        
        # Library list
        layout.separator()
        row = layout.row()
        row.template_list(
            "PROREF_UL_LibraryList",
            "",
            settings,
            "linked_libraries",
            settings,
            "library_active_index",
            rows=5
        )
        
        # Library details
        if settings.linked_libraries and settings.library_active_index < len(settings.linked_libraries):
            lib = settings.linked_libraries[settings.library_active_index]
            
            box = layout.box()
            box.label(text="Library Details:", icon='INFO')
            
            col = box.column(align=True)
            col.label(text=f"Name: {lib.library_name}")
            col.label(text=f"Overrides: {lib.override_count}")
            
            # v1.5: Version info
            if lib.version_number > 0:
                col.label(text=f"Version: v{lib.version_number:02d}")
                if lib.has_newer_version:
                    col.label(text="Update available!", icon='INFO')
            
            col.label(text=f"Status: {'✓ Found' if lib.exists else '✗ Missing'}")
            
            if lib.file_size:
                col.label(text=f"Size: {lib.file_size}")
            
            col.separator()
            col.label(text="File Path:")
            col.label(text=lib.filepath, icon='FILE_FOLDER')
            
            # Actions
            col = layout.column(align=True)
            col.scale_y = 1.2
            
            op = col.operator("proref.relocate_library", text="Relocate File", icon='FILEBROWSER')
            op.library_name = lib.library_name
            
            if lib.exists:
                # Reload button (only if file exists)
                library = bpy.data.libraries.get(lib.library_name)
                if library:
                    col.operator_context = 'EXEC_DEFAULT'
                    op = col.operator("wm.lib_reload", text="Reload Library", icon='FILE_REFRESH')
                    op.library = library.name


class PROREF_PT_BatchOperations(Panel):
    """v1.5: Batch operations panel"""
    bl_label = "Batch Operations"
    bl_idname = "PROREF_PT_batch_operations"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pro Ref"
    bl_parent_id = "PROREF_PT_reference_manager"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.proref_settings
        
        # Count selected
        selected_count = sum(1 for lib in settings.linked_libraries if lib.selected)
        
        if selected_count == 0:
            layout.label(text="Select libraries above", icon='INFO')
            layout.label(text="Use checkboxes to select")
            return
        
        # Show selection count
        box = layout.box()
        box.label(text=f"{selected_count} libraries selected", icon='CHECKMARK')
        
        # Batch Reload
        box = layout.box()
        box.label(text="Batch Reload:", icon='FILE_REFRESH')
        col = box.column(align=True)
        col.scale_y = 1.2
        col.operator("proref.batch_reload_libraries", text="Reload All Selected", icon='FILE_REFRESH')
        
        # Batch Relink
        box = layout.box()
        box.label(text="Batch Relink:", icon='FILEBROWSER')
        col = box.column(align=True)
        col.scale_y = 1.2
        col.operator("proref.batch_relink", text="Find & Replace Paths", icon='FILE_REFRESH')
        col.operator("proref.batch_search_folder", text="Search Folder", icon='VIEWZOOM')
        
        # Version Operations
        box = layout.box()
        box.label(text="Version Control:", icon='SORTTIME')
        col = box.column(align=True)
        col.scale_y = 1.2
        col.operator("proref.detect_versions", text="Detect Versions", icon='ZOOM_IN')
        
        # Show bump button only if updates available
        updates_available = sum(1 for lib in settings.linked_libraries 
                               if lib.selected and lib.has_newer_version)
        
        if updates_available > 0:
            row = col.row()
            row.alert = True
            row.operator("proref.bump_to_latest", text=f"Bump to Latest ({updates_available})", icon='TRIA_UP')
        else:
            col.operator("proref.bump_to_latest", text="Bump to Latest", icon='TRIA_UP')


class PROREF_PT_CLITools(Panel):
    """v1.5: CLI/Headless tools panel"""
    bl_label = "CLI Tools"
    bl_idname = "PROREF_PT_cli_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pro Ref"
    bl_parent_id = "PROREF_PT_reference_manager"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.proref_settings
        
        box = layout.box()
        box.label(text="Headless Mode Tools:", icon='CONSOLE')
        
        col = box.column(align=True)
        col.operator("proref.cli_auto_fix", text="Auto-Fix Links", icon='TOOL_SETTINGS')
        col.operator("proref.cli_report", text="Print Report", icon='TEXT')
        col.operator("proref.cli_validate", text="Validate Libraries", icon='CHECKMARK')
        
        layout.separator()
        
        # Settings
        box = layout.box()
        box.label(text="CLI Settings:", icon='PREFERENCES')
        col = box.column()
        col.prop(settings, "auto_fix_on_load")
        col.prop(settings, "use_environment_variables")
        
        # Info box
        box = layout.box()
        box.label(text="Environment Variables:", icon='INFO')
        col = box.column(align=True)
        col.scale_y = 0.8
        col.label(text="Use ${VAR_NAME} in paths")
        col.label(text="Example: ${PROJECT_DIR}/char.blend")


class PROREF_PT_QuickActions(Panel):
    """Quick actions for selected override"""
    bl_label = "Quick Actions"
    bl_idname = "PROREF_PT_quick_actions"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pro Ref"
    bl_parent_id = "PROREF_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        if not obj:
            layout.label(text="No active object", icon='INFO')
            return
        
        if not obj.override_library:
            layout.label(text="Not a library override", icon='INFO')
            return
        
        # Quick info
        box = layout.box()
        box.label(text=f"Override: {obj.name}", icon='LINKED')
        
        if obj.override_library.reference:
            ref = obj.override_library.reference
            box.label(text=f"Reference: {ref.name}")
            
            if ref.library:
                box.label(text=f"Library: {ref.library.name}")
        
        # Quick actions
        col = layout.column(align=True)
        col.scale_y = 1.2
        
        col.operator("proref.make_all_editable", text="Make All Editable", icon='UNLOCKED')
        col.operator("proref.repair_override", text="Repair Issues", icon='TOOL_SETTINGS')
        col.operator("proref.resync_override", text="Resync Override", icon='FILE_REFRESH')
        
        # Danger zone
        box = layout.box()
        box.label(text="Danger Zone:", icon='ERROR')
        col = box.column(align=True)
        col.alert = True
        col.operator("outliner.liboverride_operation", text="Clear Override").type = 'OVERRIDE_LIBRARY_CLEAR_SINGLE'


# Registration
classes = (
    PROREF_UL_LibraryList,
    PROREF_PT_ReferenceManager,
    PROREF_PT_BatchOperations,  # v1.5
    PROREF_PT_CLITools,         # v1.5
    PROREF_PT_QuickActions,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
