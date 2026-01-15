"""
Professional Referencing & Rig UI - Version Utilities
Handles version detection, comparison, and file scanning
"""

import re
import os
from pathlib import Path

class VersionUtils:
    """Utilities for detecting and managing asset versions"""
    
    # Supported version naming patterns
    VERSION_PATTERNS = [
        (r'[._-]v(\d+)', '_v'),           # character_v01.blend
        (r'[._-]ver(\d+)', '_ver'),       # character_ver01.blend
        (r'[._-]version(\d+)', '_version'),# character_version01.blend
        (r'\.v(\d+)\.', '.v'),            # character.v01.blend
        (r'-v(\d+)', '-v'),               # character-v01.blend
    ]
    
    @staticmethod
    def extract_version(filepath):
        """
        Extract version number from a filepath
        
        Args:
            filepath: Path to check for version number
            
        Returns:
            int: Version number if found, None otherwise
        """
        filename = os.path.basename(filepath)
        
        for pattern, _ in VersionUtils.VERSION_PATTERNS:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    @staticmethod
    def get_version_pattern(filepath):
        """
        Get the version pattern used in a filepath
        
        Args:
            filepath: Path to analyze
            
        Returns:
            str: Pattern identifier (e.g., '_v', '-v') or None
        """
        filename = os.path.basename(filepath)
        
        for pattern, identifier in VersionUtils.VERSION_PATTERNS:
            if re.search(pattern, filename, re.IGNORECASE):
                return identifier
        
        return None
    
    @staticmethod
    def get_base_name(filepath):
        """
        Get the base filename without version number
        
        Args:
            filepath: Path to process
            
        Returns:
            str: Base filename without version
        """
        path = Path(filepath)
        stem = path.stem
        
        # Remove version pattern
        for pattern, _ in VersionUtils.VERSION_PATTERNS:
            stem = re.sub(pattern, '', stem, flags=re.IGNORECASE)
        
        return stem
    
    @staticmethod
    def find_all_versions(filepath):
        """
        Find all versions of a file in the same directory
        
        Args:
            filepath: Path to the reference file
            
        Returns:
            list: List of tuples (filepath, version_number)
        """
        if not os.path.exists(filepath):
            # Try to find directory from partial path
            directory = os.path.dirname(filepath)
            if not os.path.exists(directory):
                return []
        else:
            directory = os.path.dirname(filepath)
        
        path = Path(filepath)
        base_name = VersionUtils.get_base_name(filepath)
        pattern_type = VersionUtils.get_version_pattern(filepath)
        
        if not pattern_type:
            # No version pattern found
            return [(filepath, None)]
        
        # Build glob pattern
        # Example: character_v*.blend
        glob_pattern = f"{base_name}{pattern_type}*{path.suffix}"
        
        versions = []
        for file_path in Path(directory).glob(glob_pattern):
            version_num = VersionUtils.extract_version(str(file_path))
            if version_num is not None:
                versions.append((str(file_path), version_num))
        
        # Sort by version number
        versions.sort(key=lambda x: x[1] if x[1] is not None else 0)
        
        return versions
    
    @staticmethod
    def get_latest_version(filepath):
        """
        Get the path to the latest version of a file
        
        Args:
            filepath: Path to any version of the file
            
        Returns:
            tuple: (latest_filepath, version_number) or (original, None) if no versions
        """
        versions = VersionUtils.find_all_versions(filepath)
        
        if not versions:
            return (filepath, None)
        
        # Return the last item (highest version)
        return versions[-1]
    
    @staticmethod
    def has_newer_version(filepath):
        """
        Check if there's a newer version available
        
        Args:
            filepath: Current file path
            
        Returns:
            bool: True if newer version exists
        """
        current_version = VersionUtils.extract_version(filepath)
        if current_version is None:
            return False
        
        latest_path, latest_version = VersionUtils.get_latest_version(filepath)
        
        if latest_version is None:
            return False
        
        return latest_version > current_version
    
    @staticmethod
    def build_version_path(base_filepath, version_number):
        """
        Build a filepath with a specific version number
        
        Args:
            base_filepath: Original filepath (with or without version)
            version_number: Target version number
            
        Returns:
            str: New filepath with specified version
        """
        path = Path(base_filepath)
        base_name = VersionUtils.get_base_name(base_filepath)
        pattern_type = VersionUtils.get_version_pattern(base_filepath) or '_v'
        
        # Build new filename
        new_stem = f"{base_name}{pattern_type}{version_number:02d}"
        new_path = path.parent / f"{new_stem}{path.suffix}"
        
        return str(new_path)
    
    @staticmethod
    def compare_versions(path1, path2):
        """
        Compare version numbers of two files
        
        Args:
            path1: First file path
            path2: Second file path
            
        Returns:
            int: -1 if path1 < path2, 0 if equal, 1 if path1 > path2, None if incomparable
        """
        v1 = VersionUtils.extract_version(path1)
        v2 = VersionUtils.extract_version(path2)
        
        if v1 is None or v2 is None:
            return None
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    
    @staticmethod
    def get_version_info(filepath):
        """
        Get comprehensive version information about a file
        
        Args:
            filepath: Path to analyze
            
        Returns:
            dict: {
                'current_version': int or None,
                'latest_version': int or None,
                'latest_path': str,
                'has_newer': bool,
                'all_versions': list of tuples,
                'pattern_type': str or None
            }
        """
        current_version = VersionUtils.extract_version(filepath)
        latest_path, latest_version = VersionUtils.get_latest_version(filepath)
        all_versions = VersionUtils.find_all_versions(filepath)
        pattern_type = VersionUtils.get_version_pattern(filepath)
        
        has_newer = False
        if current_version is not None and latest_version is not None:
            has_newer = latest_version > current_version
        
        return {
            'current_version': current_version,
            'latest_version': latest_version,
            'latest_path': latest_path,
            'has_newer': has_newer,
            'all_versions': all_versions,
            'pattern_type': pattern_type,
        }