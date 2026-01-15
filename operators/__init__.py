"""
Professional Referencing & Rig UI - Operators Module
All operator classes for the addon
"""

import bpy

# Import operator modules
from . import smart_link
from . import rig_ui_manager
from . import override_health
from . import batch_operations  # v1.5

# Module list
modules = [
    smart_link,
    rig_ui_manager,
    override_health,
    batch_operations,  # v1.5
]

def register():
    """Register all operator classes"""
    for module in modules:
        if hasattr(module, 'register'):
            module.register()

def unregister():
    """Unregister all operator classes"""
    for module in reversed(modules):
        if hasattr(module, 'unregister'):
            module.unregister()
