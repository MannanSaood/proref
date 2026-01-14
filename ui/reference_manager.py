"""
Professional Referencing & Rig UI - Reference Manager Panel
Visual management interface for linked libraries with batch operations
"""

import bpy
import os
from bpy.types import Panel, UIList


class PROREF_UL_LibraryList(UIList):
    """Enhanced UI List for displaying linked libraries"""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            
            # Selection checkbox for batch operations
            row.prop(item, "is_selected", text="")
            
            # Library status icon
            if item.exists:
                status_icon = 'CHECKMARK'
            else:
                status_icon = 'ERROR'
            
            # Main info
            sub = row.row()
            sub.label(text=item.library_name, icon=status_icon)
            
            # Override count badge
            sub = row.row()
            sub.alignment = 'RIGHT'
            sub.label(text=f"{item.override_count}")
            
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.library_name, icon='LINKED' if item.exists else 'ERROR')


class PROREF_PT_ReferenceManager(Panel):
    """Reference Manager - Visual library overview with batch operations"""
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
        
        # Header row with refresh and stats
        row = layout.row(align=True)
        row.operator("proref.update_library_list", text="Refresh", icon='FILE_REFRESH')
        
        # Quick stats
        if settings.linked_libraries:
            total = len(settings.linked_libraries)
            missing = sum(1 for lib in settings.linked_libraries if not lib.exists)
            if missing > 0:
                row.label(text=f"{total} libs ({missing} missing)", icon='ERROR')
            else:
                row.label(text=f"{total} libraries", icon='CHECKMARK')
        
        if not settings.linked_libraries:
            box = layout.box()
            box.label(text="No linked libraries found", icon='INFO')
            box.label(text="Use 'Smart Link Character' to add", icon='ADD')
            return
        
        # Library list with selection checkboxes
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
        
        # Batch operations sidebar
        col = row.column(align=True)
        col.operator("proref.select_all_libraries", text="", icon='CHECKBOX_HLT')
        col.operator("proref.deselect_all_libraries", text="", icon='CHECKBOX_DEHLT')
        col.separator()
        col.operator("proref.batch_reload_libraries", text="", icon='FILE_REFRESH')
        
        # Selected library details
        if settings.library_active_index < len(settings.linked_libraries):
            lib = settings.linked_libraries[settings.library_active_index]
            self._draw_library_details(layout, lib)
    
    def _draw_library_details(self, layout, lib):
        """Draw detailed info for selected library"""
        box = layout.box()
        
        # Header with status
        row = box.row()
        if lib.exists:
            row.label(text=lib.library_name, icon='LINKED')
        else:
            row.label(text=lib.library_name, icon='ERROR')
            row.label(text="MISSING", icon='BLANK1')
        
        # Details grid
        col = box.column(align=True)
        
        # File info row
        row = col.row()
        row.label(text=f"Overrides: {lib.override_count}")
        if lib.file_size:
            row.label(text=f"Size: {lib.file_size}")
        
        # Modified date
        if lib.last_modified:
            col.label(text=f"Modified: {lib.last_modified}", icon='TIME')
        
        # Path (truncated if too long)
        col.separator()
        filepath = lib.filepath
        if len(filepath) > 50:
            filepath = "..." + filepath[-47:]
        col.label(text=filepath, icon='FILE_FOLDER')
        
        # Action buttons
        col = layout.column(align=True)
        col.scale_y = 1.2
        
        # Relocate button (always available)
        op = col.operator("proref.relocate_library", text="Relocate File", icon='FILEBROWSER')
        op.library_name = lib.library_name
        
        # Reload button (only if file exists)
        if lib.exists:
            op = col.operator("proref.reload_library", text="Reload Library", icon='FILE_REFRESH')
            op.library_name = lib.library_name


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
    PROREF_PT_QuickActions,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
