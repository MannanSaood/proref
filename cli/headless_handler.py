"""
Professional Referencing & Rig UI - Headless Handler
Support for Blender background/headless mode (render farms)
"""

import bpy
import os
from bpy.app.handlers import persistent

class HeadlessHandler:
    """Handles addon behavior when running in background mode"""
    
    @staticmethod
    def is_headless():
        """Check if Blender is running in background mode"""
        return bpy.app.background
    
    @staticmethod
    def resolve_environment_path(filepath):
        """
        Resolve environment variables in file paths
        
        Supports patterns like:
        - ${PROJECT_DIR}/assets/char.blend
        - $USER_DIR/project/char.blend
        - %USERPROFILE%\\project\\char.blend (Windows)
        
        Args:
            filepath: Path potentially containing environment variables
            
        Returns:
            str: Resolved path
        """
        # Expand environment variables
        resolved = os.path.expandvars(filepath)
        
        # Also try expanduser for ~ paths
        resolved = os.path.expanduser(resolved)
        
        return resolved
    
    @staticmethod
    def auto_fix_broken_links(report_only=False):
        """
        Automatically fix broken library links using environment variables
        
        Args:
            report_only: If True, only report issues without fixing
            
        Returns:
            dict: Statistics about fixed/missing libraries
        """
        stats = {
            'total': 0,
            'fixed': 0,
            'missing': 0,
            'already_ok': 0
        }
        
        for library in bpy.data.libraries:
            stats['total'] += 1
            
            # Get absolute path
            abs_path = bpy.path.abspath(library.filepath)
            
            # Check if file exists
            if os.path.exists(abs_path):
                stats['already_ok'] += 1
                continue
            
            # Try resolving with environment variables
            resolved_path = HeadlessHandler.resolve_environment_path(library.filepath)
            
            if os.path.exists(resolved_path):
                if not report_only:
                    library.filepath = resolved_path
                    try:
                        library.reload()
                        stats['fixed'] += 1
                        print(f"[ProRef] Fixed: {library.name} -> {resolved_path}")
                    except Exception as e:
                        stats['missing'] += 1
                        print(f"[ProRef] Failed to reload: {library.name} - {e}")
                else:
                    stats['fixed'] += 1
                    print(f"[ProRef] Can fix: {library.name} -> {resolved_path}")
            else:
                stats['missing'] += 1
                print(f"[ProRef] Missing: {library.name} (tried: {resolved_path})")
        
        return stats
    
    @staticmethod
    def print_library_report():
        """Print a report of all libraries in the scene"""
        print("\n" + "="*70)
        print("PROFESSIONAL REFERENCING - LIBRARY REPORT")
        print("="*70)
        
        if not bpy.data.libraries:
            print("No libraries found in scene")
            return
        
        print(f"\nTotal Libraries: {len(bpy.data.libraries)}\n")
        
        for library in bpy.data.libraries:
            abs_path = bpy.path.abspath(library.filepath)
            exists = os.path.exists(abs_path)
            
            status = "✓" if exists else "✗"
            print(f"{status} {library.name}")
            print(f"  Path: {library.filepath}")
            
            if not exists:
                # Try environment variable resolution
                resolved = HeadlessHandler.resolve_environment_path(library.filepath)
                if os.path.exists(resolved):
                    print(f"  Can fix: {resolved}")
                else:
                    print(f"  Missing (tried: {resolved})")
            
            print()
        
        print("="*70 + "\n")
    
    @staticmethod
    def validate_scene_libraries():
        """
        Validate all libraries and return status
        
        Returns:
            bool: True if all libraries are valid, False otherwise
        """
        if not bpy.data.libraries:
            return True
        
        all_valid = True
        
        for library in bpy.data.libraries:
            abs_path = bpy.path.abspath(library.filepath)
            
            if not os.path.exists(abs_path):
                # Try resolving
                resolved = HeadlessHandler.resolve_environment_path(library.filepath)
                if not os.path.exists(resolved):
                    all_valid = False
        
        return all_valid


# Persistent handler for auto-fixing on file load
@persistent
def auto_fix_on_load(dummy):
    """Handler that runs after file load in headless mode"""
    if not bpy.app.background:
        return
    
    print("[ProRef] Running in headless mode - checking libraries...")
    
    stats = HeadlessHandler.auto_fix_broken_links(report_only=False)
    
    print(f"[ProRef] Library Status: {stats['already_ok']} OK, "
          f"{stats['fixed']} fixed, {stats['missing']} missing")
    
    if stats['missing'] > 0:
        print(f"[ProRef] WARNING: {stats['missing']} libraries could not be found")


# Operator for manual CLI control
class PROREF_OT_CLIAutoFix(bpy.types.Operator):
    """Fix broken library links (CLI mode)"""
    bl_idname = "proref.cli_auto_fix"
    bl_label = "CLI Auto-Fix Links"
    bl_description = "Automatically fix broken library links using environment variables"
    
    report_only: bpy.props.BoolProperty(
        name="Report Only",
        description="Only report issues without fixing",
        default=False
    )
    
    def execute(self, context):
        stats = HeadlessHandler.auto_fix_broken_links(self.report_only)
        
        msg = f"Fixed {stats['fixed']} libraries"
        if stats['missing'] > 0:
            msg += f" ({stats['missing']} missing)"
        
        self.report({'INFO'}, msg)
        return {'FINISHED'}


class PROREF_OT_CLIReport(bpy.types.Operator):
    """Print library report to console"""
    bl_idname = "proref.cli_report"
    bl_label = "CLI Library Report"
    bl_description = "Print a detailed report of all libraries to the console"
    
    def execute(self, context):
        HeadlessHandler.print_library_report()
        return {'FINISHED'}


class PROREF_OT_CLIValidate(bpy.types.Operator):
    """Validate all libraries"""
    bl_idname = "proref.cli_validate"
    bl_label = "CLI Validate Libraries"
    bl_description = "Validate that all libraries can be found"
    
    def execute(self, context):
        is_valid = HeadlessHandler.validate_scene_libraries()
        
        if is_valid:
            self.report({'INFO'}, "All libraries are valid")
        else:
            self.report({'ERROR'}, "Some libraries are missing or invalid")
        
        return {'FINISHED'}


# Registration
classes = (
    PROREF_OT_CLIAutoFix,
    PROREF_OT_CLIReport,
    PROREF_OT_CLIValidate,
)

def register():
    """Register CLI operators and handlers"""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register auto-fix handler
    if auto_fix_on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(auto_fix_on_load)
    
    if bpy.app.background:
        print("[ProRef] Headless mode detected - auto-fix enabled")

def unregister():
    """Unregister CLI components"""
    # Remove handler
    if auto_fix_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(auto_fix_on_load)
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)