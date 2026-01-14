"""
Professional Referencing & Rig UI - UI Module
All panel and UI classes
"""

import bpy

# Import UI modules
from . import main_panel
from . import reference_manager
from . import preferences

# Module list
modules = [
    main_panel,
    reference_manager,
    preferences,
]

def register():
    """Register all UI classes"""
    for module in modules:
        if hasattr(module, 'register'):
            module.register()

def unregister():
    """Unregister all UI classes"""
    for module in reversed(modules):
        if hasattr(module, 'unregister'):
            module.unregister()
