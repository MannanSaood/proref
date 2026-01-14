"""
Professional Referencing & Rig UI
Industry-grade character linking, override management, and rig UI handling for Blender
"""

bl_info = {
    "name": "Professional Referencing & Rig UI",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Pro Ref",
    "description": "Industry-grade character linking, override management, and rig UI handling",
    "warning": "",
    "doc_url": "https://github.com/yourusername/professional_referencing",
    "category": "Rigging",
}

import bpy
from bpy.props import PointerProperty

# Import all modules
from . import properties
from . import operators
from . import ui

# Module list for registration
modules = [
    properties,
    operators,
    ui,
]

# Keyboard shortcut keymaps
addon_keymaps = []


def register_keymaps():
    """Register keyboard shortcuts"""
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if kc:
        # 3D View keymap
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        
        # Ctrl+Shift+L - Smart Link Character
        kmi = km.keymap_items.new(
            'proref.smart_link',
            type='L',
            value='PRESS',
            ctrl=True,
            shift=True
        )
        addon_keymaps.append((km, kmi))
        
        # Ctrl+Shift+H - Run Health Check
        kmi = km.keymap_items.new(
            'proref.health_check',
            type='H',
            value='PRESS',
            ctrl=True,
            shift=True
        )
        addon_keymaps.append((km, kmi))
        
        # Ctrl+Shift+R - Execute Rig UI
        kmi = km.keymap_items.new(
            'proref.execute_rig_ui',
            type='R',
            value='PRESS',
            ctrl=True,
            shift=True
        )
        addon_keymaps.append((km, kmi))
        
        # Ctrl+Shift+E - Make All Editable
        kmi = km.keymap_items.new(
            'proref.make_all_editable',
            type='E',
            value='PRESS',
            ctrl=True,
            shift=True
        )
        addon_keymaps.append((km, kmi))


def unregister_keymaps():
    """Unregister keyboard shortcuts"""
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    """Register all classes and properties"""
    # Register all modules
    for module in modules:
        if hasattr(module, 'register'):
            module.register()
    
    # Register scene properties
    bpy.types.Scene.proref_settings = PointerProperty(
        type=properties.ProRefSceneSettings
    )
    
    # Register keyboard shortcuts
    register_keymaps()
    
    print("Professional Referencing & Rig UI: Registered successfully")


def unregister():
    """Unregister all classes and properties"""
    # Unregister keyboard shortcuts
    unregister_keymaps()
    
    # Remove scene properties
    if hasattr(bpy.types.Scene, 'proref_settings'):
        del bpy.types.Scene.proref_settings
    
    # Unregister all modules in reverse order
    for module in reversed(modules):
        if hasattr(module, 'unregister'):
            module.unregister()
    
    print("Professional Referencing & Rig UI: Unregistered")


if __name__ == "__main__":
    register()
