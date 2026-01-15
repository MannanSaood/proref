"""
Professional Referencing & Rig UI - CLI Module
Command-line and headless mode support
"""

import bpy

# Import CLI modules
from . import headless_handler

def register():
    """Register CLI components"""
    headless_handler.register()

def unregister():
    """Unregister CLI components"""
    headless_handler.unregister()