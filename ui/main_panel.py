"""
Professional Referencing & Rig UI - Main Panel
Primary user interface in 3D viewport sidebar
"""

import bpy
from bpy.types import Panel

class PROREF_PT_MainPanel(Panel):
    """Main panel for Professional Referencing"""
    bl_label = "Pro Referencing"
    bl_idname = "PROREF_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pro Ref"
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.proref_settings
        
        # Header with version info
        box = layout.box()
        box.label(text="Professional Referencing v1.0", icon='LINKED')
        
        # Quick Stats
        override_count = sum(1 for obj in bpy.data.objects if obj.override_library)
        library_count = len(bpy.data.libraries)
        
        row = box.row(align=True)
        row.label(text=f"Overrides: {override_count}")
        row.label(text=f"Libraries: {library_count}")


class PROREF_PT_LinkingPanel(Panel):
    """Character linking section"""
    bl_label = "Character Linking"
    bl_idname = "PROREF_PT_linking_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pro Ref"
    bl_parent_id = "PROREF_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.proref_settings
        
        # Link Operations
        col = layout.column(align=True)
        col.scale_y = 1.2
        col.operator("proref.smart_link", text="Smart Link Character", icon='ADD')
        col.operator("proref.batch_link", text="Batch Link", icon='DOCUMENTS')
        
        # Settings
        box = layout.box()
        box.label(text="Link Settings:", icon='PREFERENCES')
        
        col = box.column(align=True)
        col.prop(settings, "auto_make_editable")
        col.prop(settings, "unique_rig_ui_names")
        col.prop(settings, "auto_execute_rig_ui")
        col.prop(settings, "selective_override_armature_only")
        
        if settings.show_advanced_options:
            col.separator()
            col.prop(settings, "make_bones_editable")
            col.prop(settings, "make_constraints_editable")


class PROREF_PT_RigUIPanel(Panel):
    """Rig UI management section"""
    bl_label = "Rig UI Management"
    bl_idname = "PROREF_PT_rigui_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pro Ref"
    bl_parent_id = "PROREF_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        
        # Check if active object has rig UI
        has_rig_ui = False
        script_name = None
        
        if obj:
            if obj.type == 'ARMATURE' and "proref_rig_ui" in obj:
                has_rig_ui = True
                script_name = obj["proref_rig_ui"]
            else:
                # Check children for armature
                for child in obj.children_recursive:
                    if child.type == 'ARMATURE' and "proref_rig_ui" in child:
                        has_rig_ui = True
                        script_name = child["proref_rig_ui"]
                        break
        
        # Execution Controls
        col = layout.column(align=True)
        col.scale_y = 1.2
        
        if has_rig_ui:
            col.operator("proref.execute_rig_ui", text="Execute Rig UI", icon='PLAY')
            col.operator("proref.validate_rig_ui", text="Validate Script", icon='CHECKMARK')
            
            box = layout.box()
            box.label(text=f"Script: {script_name}", icon='SCRIPT')
        else:
            col.operator("proref.execute_rig_ui", text="Execute Rig UI", icon='PLAY')
            col.enabled = False
            layout.label(text="No rig UI found", icon='INFO')
        
        layout.separator()
        
        # Batch operations
        col = layout.column(align=True)
        col.operator("proref.refresh_all_rig_ui", text="Refresh All", icon='FILE_REFRESH')
        col.operator("proref.create_rig_ui_template", text="Create Template", icon='ADD')


class PROREF_PT_HealthPanel(Panel):
    """Override health monitoring section"""
    bl_label = "Override Health"
    bl_idname = "PROREF_PT_health_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pro Ref"
    bl_parent_id = "PROREF_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.proref_settings
        
        # Health Check Button
        row = layout.row()
        row.scale_y = 1.5
        row.operator("proref.health_check", text="Run Health Check", icon='CHECKMARK')
        
        # Filters
        if settings.health_checks:
            box = layout.box()
            row = box.row(align=True)
            row.prop(settings, "filter_healthy_only", text="Healthy", toggle=True)
            row.prop(settings, "filter_errors_only", text="Errors", toggle=True)
        
        # Health Results
        if settings.health_checks:
            box = layout.box()
            box.label(text=f"Results ({len(settings.health_checks)}):", icon='INFO')
            
            # Count by status
            healthy = sum(1 for h in settings.health_checks if h.health_status == 'HEALTHY')
            warnings = sum(1 for h in settings.health_checks if h.health_status == 'WARNING')
            errors = sum(1 for h in settings.health_checks if h.health_status == 'ERROR')
            
            row = box.row(align=True)
            row.label(text=f"✓ {healthy}", icon='CHECKMARK')
            row.label(text=f"⚠ {warnings}", icon='ERROR')
            row.label(text=f"✗ {errors}", icon='CANCEL')
            
            # List health checks
            for health in settings.health_checks:
                # Apply filters
                if settings.filter_healthy_only and health.health_status != 'HEALTHY':
                    continue
                if settings.filter_errors_only and health.health_status != 'ERROR':
                    continue
                
                box = layout.box()
                
                # Status icon
                if health.health_status == 'HEALTHY':
                    icon = 'CHECKMARK'
                elif health.health_status == 'WARNING':
                    icon = 'ERROR'
                else:
                    icon = 'CANCEL'
                
                row = box.row()
                row.label(text=health.armature_name, icon=icon)
                
                if health.issue_count > 0:
                    row = box.row()
                    row.label(text=f"{health.issue_count} issues", icon='INFO')
                    
                    if health.issue_description:
                        row = box.row()
                        row.scale_y = 0.8
                        row.label(text=health.issue_description)
                
                # Action buttons
                row = box.row(align=True)
                row.scale_y = 0.9
                
                op = row.operator("proref.repair_override", text="Repair", icon='TOOL_SETTINGS')
                op.object_name = health.object_name
                
                op = row.operator("proref.resync_override", text="Resync", icon='FILE_REFRESH')
                op.object_name = health.object_name


class PROREF_PT_SettingsPanel(Panel):
    """Advanced settings panel"""
    bl_label = "Advanced Settings"
    bl_idname = "PROREF_PT_settings_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pro Ref"
    bl_parent_id = "PROREF_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        settings = context.scene.proref_settings
        
        layout.prop(settings, "show_advanced_options")
        
        if settings.show_advanced_options:
            box = layout.box()
            box.label(text="Override Settings:", icon='MODIFIER')
            col = box.column(align=True)
            col.prop(settings, "make_bones_editable")
            col.prop(settings, "make_constraints_editable")


# Registration
classes = (
    PROREF_PT_MainPanel,
    PROREF_PT_LinkingPanel,
    PROREF_PT_RigUIPanel,
    PROREF_PT_HealthPanel,
    PROREF_PT_SettingsPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
