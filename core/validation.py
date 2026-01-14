"""
Professional Referencing & Rig UI - Override Validation Module
Detects issues, validates health, and diagnoses common override problems
"""

import bpy
import os


class OverrideValidator:
    """Validates library overrides and provides diagnostic utilities"""
    
    @staticmethod
    def find_all_overrides_in_scene():
        """
        Find all library override objects in the current scene
        
        Returns:
            list: Objects with override_library set
        """
        return [obj for obj in bpy.data.objects if obj.override_library]
    
    @staticmethod
    def check_override_health(obj):
        """
        Perform comprehensive health check on a library override
        
        Args:
            obj: Object with override_library
            
        Returns:
            dict: Health check results
        """
        result = {
            'is_healthy': True,
            'issues': [],
            'warnings': [],
            'info': {}
        }
        
        if not obj.override_library:
            result['is_healthy'] = False
            result['issues'].append("Object is not a library override")
            return result
        
        override = obj.override_library
        
        # Check 1: Reference exists
        if not override.reference:
            result['is_healthy'] = False
            result['issues'].append("Override reference is missing")
        else:
            result['info']['reference_name'] = override.reference.name
        
        # Check 2: Library file exists
        library_check = OverrideValidator._check_library_status(override)
        result['issues'].extend(library_check['issues'])
        result['info'].update(library_check['info'])
        if library_check['issues']:
            result['is_healthy'] = False
        
        # Check 3: Override properties
        prop_count = len(override.properties) if hasattr(override, 'properties') else 0
        result['info']['override_property_count'] = prop_count
        if prop_count == 0:
            result['warnings'].append("No override properties - may not be editable")
        
        # Check 4: Armature-specific checks
        if obj.type == 'ARMATURE':
            armature_check = OverrideValidator._check_armature_status(obj)
            result['warnings'].extend(armature_check['warnings'])
            result['info'].update(armature_check['info'])
        
        # Check 5: Rig UI status
        result['info']['has_rig_ui'] = "proref_rig_ui" in obj
        
        return result
    
    @staticmethod
    def _check_library_status(override):
        """Check library file status for an override"""
        result = {'issues': [], 'info': {}}
        
        if not override.reference or not override.reference.library:
            return result
        
        library = override.reference.library
        result['info']['library_name'] = library.name
        result['info']['library_path'] = library.filepath
        
        # Check file exists
        abs_path = bpy.path.abspath(library.filepath)
        if not os.path.exists(abs_path):
            result['issues'].append(f"Library file not found: {library.filepath}")
        else:
            result['info']['library_exists'] = True
        
        return result
    
    @staticmethod
    def _check_armature_status(armature):
        """Check armature-specific health issues"""
        result = {'warnings': [], 'info': {}}
        
        if not armature.pose:
            result['warnings'].append("Armature has no pose data")
            return result
        
        # Count bones and locked status
        bone_count = len(armature.pose.bones)
        locked_count = 0
        
        for bone in armature.pose.bones:
            if any(bone.lock_location) or any(bone.lock_rotation) or any(bone.lock_scale):
                locked_count += 1
        
        result['info']['bone_count'] = bone_count
        result['info']['locked_bone_count'] = locked_count
        
        if locked_count > bone_count * 0.5:
            result['warnings'].append(f"Many bones locked ({locked_count}/{bone_count})")
        
        # Count constraint issues
        constraint_issues = 0
        for bone in armature.pose.bones:
            for constraint in bone.constraints:
                if constraint.mute:
                    continue
                if hasattr(constraint, 'target') and constraint.target is None:
                    if constraint.type not in ['LIMIT_LOCATION', 'LIMIT_ROTATION', 'LIMIT_SCALE']:
                        constraint_issues += 1
        
        result['info']['constraint_issues'] = constraint_issues
        if constraint_issues > 0:
            result['warnings'].append(f"{constraint_issues} constraints missing targets")
        
        return result
    
    @staticmethod
    def diagnose_common_issues(obj):
        """
        Diagnose common override issues with actionable solutions
        
        Args:
            obj: Object to diagnose
            
        Returns:
            list: [(issue_type, description, severity), ...]
        """
        issues = []
        
        if not obj.override_library:
            return [('NOT_OVERRIDE', "Object is not a library override", 'ERROR')]
        
        override = obj.override_library
        
        # Issue 1: Missing reference
        if not override.reference:
            issues.append((
                'MISSING_REFERENCE',
                "Override reference missing - linked object may be deleted",
                'ERROR'
            ))
        
        # Issue 2: Library file missing
        if override.reference and override.reference.library:
            library = override.reference.library
            abs_path = bpy.path.abspath(library.filepath)
            if not os.path.exists(abs_path):
                issues.append((
                    'LIBRARY_NOT_FOUND',
                    f"Library file missing: {abs_path}",
                    'ERROR'
                ))
        
        # Issue 3: No editable properties
        prop_count = len(override.properties) if hasattr(override, 'properties') else 0
        if prop_count == 0:
            issues.append((
                'NO_EDITABLE_PROPS',
                "No editable properties - use 'Make All Editable'",
                'WARNING'
            ))
        
        # Issue 4: System override flag (Blender 3.0+)
        if hasattr(override, 'is_system_override') and override.is_system_override:
            issues.append((
                'SYSTEM_OVERRIDE',
                "System-generated override - may need resync",
                'INFO'
            ))
        
        return issues
    
    @staticmethod
    def validate_library_path(library):
        """
        Validate a library file path is accessible and valid
        
        Args:
            library: bpy.types.Library
            
        Returns:
            tuple: (is_valid, message)
        """
        if not library:
            return (False, "No library provided")
        
        abs_path = bpy.path.abspath(library.filepath)
        
        # Check existence
        if not os.path.exists(abs_path):
            return (False, f"File not found: {abs_path}")
        
        if not os.path.isfile(abs_path):
            return (False, f"Not a file: {abs_path}")
        
        if not abs_path.endswith('.blend'):
            return (False, f"Not a .blend file: {abs_path}")
        
        # Validate header
        try:
            with open(abs_path, 'rb') as f:
                header = f.read(12)
                if not header.startswith(b'BLENDER'):
                    return (False, "Invalid Blender file header")
        except PermissionError:
            return (False, f"Permission denied: {abs_path}")
        except Exception as e:
            return (False, f"Read error: {str(e)}")
        
        return (True, "Valid library path")
    
    @staticmethod
    def find_broken_overrides():
        """
        Find all broken overrides in the current file
        
        Returns:
            list: [(object, issues), ...] for objects with ERROR-level issues
        """
        broken = []
        
        for obj in bpy.data.objects:
            if not obj.override_library:
                continue
            
            issues = OverrideValidator.diagnose_common_issues(obj)
            errors = [i for i in issues if i[2] == 'ERROR']
            
            if errors:
                broken.append((obj, errors))
        
        return broken
    
    @staticmethod
    def get_override_summary(obj):
        """
        Quick summary of override status
        
        Args:
            obj: Object with override
            
        Returns:
            dict or None: Summary info
        """
        if not obj.override_library:
            return None
        
        override = obj.override_library
        
        return {
            'object_name': obj.name,
            'object_type': obj.type,
            'has_reference': override.reference is not None,
            'reference_name': override.reference.name if override.reference else None,
            'library_name': override.reference.library.name if override.reference and override.reference.library else None,
            'property_count': len(override.properties) if hasattr(override, 'properties') else 0,
        }
