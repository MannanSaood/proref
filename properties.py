"""
Professional Referencing & Rig UI - Properties Module
All PropertyGroup definitions and scene settings
"""

import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    EnumProperty,
    CollectionProperty,
)

class OverrideHealthData(PropertyGroup):
    """Stores health check data for individual library overrides"""
    
    object_name: StringProperty(
        name="Object Name",
        description="Name of the override object"
    )
    
    armature_name: StringProperty(
        name="Armature Name",
        description="Name of the armature (if applicable)"
    )
    
    health_status: EnumProperty(
        name="Health Status",
        items=[
            ('HEALTHY', "Healthy", "No issues detected"),
            ('WARNING', "Warning", "Minor issues detected"),
            ('ERROR', "Error", "Critical issues detected"),
        ],
        default='HEALTHY'
    )
    
    issue_count: IntProperty(
        name="Issue Count",
        default=0,
        min=0
    )
    
    issue_description: StringProperty(
        name="Issues",
        description="Description of detected issues"
    )
    
    locked_bone_count: IntProperty(
        name="Locked Bones",
        default=0,
        min=0
    )
    
    has_rig_ui: BoolProperty(
        name="Has Rig UI",
        default=False
    )
    
    library_path: StringProperty(
        name="Library Path",
        description="Path to the source library file"
    )
    
    library_exists: BoolProperty(
        name="Library File Exists",
        default=True
    )

class LinkedLibraryData(PropertyGroup):
    """Stores information about linked libraries in the scene"""
    
    library_name: StringProperty(
        name="Library Name"
    )
    
    filepath: StringProperty(
        name="File Path"
    )
    
    exists: BoolProperty(
        name="File Exists",
        default=True
    )
    
    override_count: IntProperty(
        name="Override Count",
        default=0,
        min=0
    )
    
    last_modified: StringProperty(
        name="Last Modified"
    )
    
    file_size: StringProperty(
        name="File Size",
        description="Human-readable file size"
    )
    
    is_selected: BoolProperty(
        name="Selected",
        description="Selected for batch operations",
        default=False
    )

class ProRefSceneSettings(PropertyGroup):
    """Main scene-level settings for the addon"""
    
    # Smart Link Settings
    auto_make_editable: BoolProperty(
        name="Auto Make Editable",
        description="Automatically make all override properties editable after linking",
        default=True
    )
    
    unique_rig_ui_names: BoolProperty(
        name="Unique Rig UI Names",
        description="Automatically create isolated rig UI scripts to avoid conflicts",
        default=True
    )
    
    auto_execute_rig_ui: BoolProperty(
        name="Auto Execute Rig UI",
        description="Automatically execute rig UI script after linking",
        default=False
    )
    
    selective_override_armature_only: BoolProperty(
        name="Animation Only Mode",
        description="Skip mesh overrides for better performance. Use when you only need to animate (not edit materials/modifiers)",
        default=False
    )
    
    # Override Settings
    make_bones_editable: BoolProperty(
        name="Make Bones Editable",
        description="Automatically make all bone transforms editable",
        default=True
    )
    
    make_constraints_editable: BoolProperty(
        name="Make Constraints Editable",
        description="Automatically make all constraints editable",
        default=True
    )
    
    # Health Check Data
    health_checks: CollectionProperty(
        type=OverrideHealthData,
        name="Health Checks"
    )
    
    health_check_active_index: IntProperty(
        name="Active Health Check",
        default=0
    )
    
    # Library Manager Data
    linked_libraries: CollectionProperty(
        type=LinkedLibraryData,
        name="Linked Libraries"
    )
    
    library_active_index: IntProperty(
        name="Active Library",
        default=0
    )
    
    # UI Settings
    show_advanced_options: BoolProperty(
        name="Show Advanced Options",
        description="Show advanced override and script options",
        default=False
    )
    
    # Filter Settings
    filter_healthy_only: BoolProperty(
        name="Show Healthy Only",
        description="Only show healthy overrides in health check list",
        default=False
    )
    
    filter_errors_only: BoolProperty(
        name="Show Errors Only",
        description="Only show overrides with errors",
        default=False
    )

# Registration
classes = (
    OverrideHealthData,
    LinkedLibraryData,
    ProRefSceneSettings,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
