"""
Professional Referencing & Rig UI - Addon Preferences
Global settings and configuration accessible from Edit > Preferences > Add-ons
"""

import bpy
from bpy.types import AddonPreferences
from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    IntProperty,
)


class ProRefPreferences(AddonPreferences):
    """Addon preferences accessible from Edit > Preferences > Add-ons"""
    bl_idname = "professional_referencing"
    
    # === Default Paths ===
    default_library_path: StringProperty(
        name="Default Library Path",
        description="Default folder to browse when linking characters",
        subtype='DIR_PATH',
        default=""
    )
    
    # === Linking Defaults ===
    default_auto_make_editable: BoolProperty(
        name="Auto Make Editable",
        description="Default setting for automatically making properties editable",
        default=True
    )
    
    default_animation_only_mode: BoolProperty(
        name="Animation Only Mode",
        description="Default setting for skipping mesh overrides",
        default=False
    )
    
    default_auto_execute_rig_ui: BoolProperty(
        name="Auto Execute Rig UI",
        description="Default setting for automatically executing rig UI after linking",
        default=False
    )
    
    # === UI Preferences ===
    show_advanced_by_default: BoolProperty(
        name="Show Advanced Options",
        description="Show advanced options by default in the sidebar panel",
        default=False
    )
    
    compact_ui: BoolProperty(
        name="Compact UI Mode",
        description="Use a more compact UI layout",
        default=False
    )
    
    # === Safety Settings ===
    confirm_dangerous_operations: BoolProperty(
        name="Confirm Dangerous Operations",
        description="Show confirmation dialogs before dangerous operations like clearing overrides",
        default=True
    )
    
    validate_scripts_before_execution: BoolProperty(
        name="Validate Scripts Before Execution",
        description="Check rig UI scripts for unsafe patterns before running",
        default=True
    )
    
    # === Performance ===
    max_health_check_objects: IntProperty(
        name="Max Health Check Objects",
        description="Maximum number of objects to check at once (0 = unlimited)",
        default=0,
        min=0,
        max=1000
    )
    
    # === Keyboard Shortcuts ===
    use_keyboard_shortcuts: BoolProperty(
        name="Enable Keyboard Shortcuts",
        description="Enable addon keyboard shortcuts (requires restart)",
        default=True
    )
    
    def draw(self, context):
        layout = self.layout
        
        # === Default Paths ===
        box = layout.box()
        box.label(text="Default Paths", icon='FILE_FOLDER')
        box.prop(self, "default_library_path")
        
        # === Linking Defaults ===
        box = layout.box()
        box.label(text="Linking Defaults", icon='LINKED')
        col = box.column(align=True)
        col.prop(self, "default_auto_make_editable")
        col.prop(self, "default_animation_only_mode")
        col.prop(self, "default_auto_execute_rig_ui")
        
        # === UI Preferences ===
        box = layout.box()
        box.label(text="UI Preferences", icon='PREFERENCES')
        col = box.column(align=True)
        col.prop(self, "show_advanced_by_default")
        col.prop(self, "compact_ui")
        
        # === Safety ===
        box = layout.box()
        box.label(text="Safety Settings", icon='ERROR')
        col = box.column(align=True)
        col.prop(self, "confirm_dangerous_operations")
        col.prop(self, "validate_scripts_before_execution")
        
        # === Performance ===
        box = layout.box()
        box.label(text="Performance", icon='MODIFIER')
        box.prop(self, "max_health_check_objects")
        
        # === Keyboard Shortcuts ===
        box = layout.box()
        box.label(text="Keyboard Shortcuts", icon='KEYINGSET')
        box.prop(self, "use_keyboard_shortcuts")
        
        if self.use_keyboard_shortcuts:
            col = box.column(align=True)
            col.label(text="Default Shortcuts:", icon='INFO')
            col.label(text="Ctrl+Shift+L - Smart Link Character")
            col.label(text="Ctrl+Shift+H - Run Health Check")
            col.label(text="Ctrl+Shift+R - Execute Rig UI")
            col.label(text="Ctrl+Shift+E - Make All Editable")


def get_preferences():
    """Helper to get addon preferences"""
    return bpy.context.preferences.addons.get("professional_referencing")


# Registration
classes = (
    ProRefPreferences,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
