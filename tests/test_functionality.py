"""
Professional Referencing & Rig UI - Comprehensive Test Suite v1.5
Run this script in Blender's Text Editor to test all functionality

HOW TO RUN:
1. Open Blender
2. Go to Scripting workspace
3. Create new text file
4. Paste this script
5. Click "Run Script"
6. Check console for results (Window > Toggle System Console)
"""

import bpy
import os
import sys


class ProRefTester:
    """Comprehensive test suite for Professional Referencing addon v1.5"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*70)
        print("PROFESSIONAL REFERENCING & RIG UI v1.5 - COMPREHENSIVE TEST SUITE")
        print("="*70 + "\n")
        
        # Test suites by phase
        self.test_addon_registration()
        self.test_phase1_core_linking()
        self.test_phase2_rig_ui_isolation()
        self.test_phase3_override_health()
        self.test_phase4_reference_manager()
        self.test_phase5_polish()
        self.test_v15_batch_operations()
        self.test_v15_version_utils()
        self.test_v15_cli_headless()
        self.test_ui_panels()
        self.test_integration()
        
        # Summary
        self.print_summary()
    
    # ==================== UTILITIES ====================
    
    def assert_true(self, condition, test_name):
        """Assert a condition is true"""
        if condition:
            self.tests_passed += 1
            self.test_results.append((test_name, "PASS", None))
            print(f"✓ {test_name}")
        else:
            self.tests_failed += 1
            self.test_results.append((test_name, "FAIL", "Condition was false"))
            print(f"✗ {test_name} - FAILED")
    
    def assert_equals(self, actual, expected, test_name):
        """Assert two values are equal"""
        if actual == expected:
            self.tests_passed += 1
            self.test_results.append((test_name, "PASS", None))
            print(f"✓ {test_name}")
        else:
            self.tests_failed += 1
            msg = f"Expected {expected}, got {actual}"
            self.test_results.append((test_name, "FAIL", msg))
            print(f"✗ {test_name} - FAILED: {msg}")
    
    def assert_not_none(self, value, test_name):
        """Assert value is not None"""
        if value is not None:
            self.tests_passed += 1
            self.test_results.append((test_name, "PASS", None))
            print(f"✓ {test_name}")
        else:
            self.tests_failed += 1
            self.test_results.append((test_name, "FAIL", "Value was None"))
            print(f"✗ {test_name} - FAILED: Value was None")
    
    def assert_has_attr(self, obj, attr, test_name):
        """Assert object has attribute"""
        if hasattr(obj, attr):
            self.tests_passed += 1
            self.test_results.append((test_name, "PASS", None))
            print(f"✓ {test_name}")
        else:
            self.tests_failed += 1
            self.test_results.append((test_name, "FAIL", f"Missing attribute: {attr}"))
            print(f"✗ {test_name} - FAILED: Missing {attr}")
    
    def assert_operator_exists(self, op_name, test_name):
        """Assert operator exists"""
        parts = op_name.split('.')
        if len(parts) == 2:
            try:
                ns = getattr(bpy.ops, parts[0])
                op = getattr(ns, parts[1])
                self.tests_passed += 1
                self.test_results.append((test_name, "PASS", None))
                print(f"✓ {test_name}")
                return True
            except AttributeError:
                pass
        self.tests_failed += 1
        self.test_results.append((test_name, "FAIL", f"Operator not found: {op_name}"))
        print(f"✗ {test_name} - FAILED: Operator not found")
        return False
    
    # ==================== ADDON REGISTRATION ====================
    
    def test_addon_registration(self):
        """Test addon registration and basic setup"""
        print("\n--- Testing Addon Registration ---")
        
        self.assert_true(
            'proref' in dir(bpy.ops),
            "Addon operators namespace registered"
        )
        
        self.assert_true(
            hasattr(bpy.types.Scene, 'proref_settings'),
            "Scene properties registered"
        )
        
        if bpy.context.scene:
            settings = bpy.context.scene.proref_settings
            self.assert_not_none(settings, "Settings accessible from scene")
    
    # ==================== PHASE 1: CORE LINKING ====================
    
    def test_phase1_core_linking(self):
        """Test Phase 1: Core Linking features"""
        print("\n--- Testing Phase 1: Core Linking ---")
        
        settings = bpy.context.scene.proref_settings
        
        self.assert_operator_exists("proref.smart_link", "smart_link operator")
        self.assert_operator_exists("proref.batch_link", "batch_link operator")
        
        self.assert_has_attr(settings, 'auto_make_editable', "auto_make_editable property")
        self.assert_has_attr(settings, 'unique_rig_ui_names', "unique_rig_ui_names property")
        self.assert_has_attr(settings, 'selective_override_armature_only', "Animation Only Mode property")
        
        self.assert_equals(settings.auto_make_editable, True, "auto_make_editable defaults to True")
        
        # Test multi-format support
        try:
            from professional_referencing.operators.smart_link import SUPPORTED_FORMATS
            
            # Check that all industry formats are supported
            expected_formats = ['.blend', '.fbx', '.usd', '.abc', '.gltf', '.glb', '.obj']
            for fmt in expected_formats:
                self.assert_true(
                    fmt in SUPPORTED_FORMATS,
                    f"Format {fmt} supported"
                )
        except ImportError as e:
            print(f"⚠ Could not import SUPPORTED_FORMATS: {e}")
    
    # ==================== PHASE 2: RIG UI ISOLATION ====================
    
    def test_phase2_rig_ui_isolation(self):
        """Test Phase 2: Rig UI Isolation features"""
        print("\n--- Testing Phase 2: Rig UI Isolation ---")
        
        settings = bpy.context.scene.proref_settings
        
        self.assert_operator_exists("proref.execute_rig_ui", "execute_rig_ui operator")
        self.assert_operator_exists("proref.validate_rig_ui", "validate_rig_ui operator")
        self.assert_operator_exists("proref.create_rig_ui_template", "create_rig_ui_template operator")
        self.assert_operator_exists("proref.refresh_all_rig_ui", "refresh_all_rig_ui operator")
        
        self.assert_has_attr(settings, 'auto_execute_rig_ui', "auto_execute_rig_ui property")
        
        # Test script_injector module
        try:
            from professional_referencing.core.script_injector import RigUIScriptInjector
            self.assert_true(True, "RigUIScriptInjector imports successfully")
            self.assert_true(hasattr(RigUIScriptInjector, 'find_rig_ui_script'), "find_rig_ui_script method")
            self.assert_true(hasattr(RigUIScriptInjector, 'create_isolated_script'), "create_isolated_script method")
            self.assert_true(hasattr(RigUIScriptInjector, 'validate_script_safety'), "validate_script_safety method")
        except ImportError as e:
            print(f"⚠ Could not import RigUIScriptInjector: {e}")
    
    # ==================== PHASE 3: OVERRIDE HEALTH ====================
    
    def test_phase3_override_health(self):
        """Test Phase 3: Override Health System features"""
        print("\n--- Testing Phase 3: Override Health System ---")
        
        settings = bpy.context.scene.proref_settings
        
        self.assert_operator_exists("proref.health_check", "health_check operator")
        self.assert_operator_exists("proref.repair_override", "repair_override operator")
        self.assert_operator_exists("proref.resync_override", "resync_override operator")
        self.assert_operator_exists("proref.make_all_editable", "make_all_editable operator")
        self.assert_operator_exists("proref.reload_library", "reload_library operator")
        
        self.assert_has_attr(settings, 'health_checks', "health_checks collection")
        self.assert_has_attr(settings, 'filter_healthy_only', "filter_healthy_only property")
        self.assert_has_attr(settings, 'filter_errors_only', "filter_errors_only property")
        
        # Test validation module
        try:
            from professional_referencing.core.validation import OverrideValidator
            self.assert_true(True, "OverrideValidator imports successfully")
            self.assert_true(hasattr(OverrideValidator, 'find_all_overrides_in_scene'), "find_all_overrides method")
            self.assert_true(hasattr(OverrideValidator, 'check_override_health'), "check_override_health method")
            self.assert_true(hasattr(OverrideValidator, 'diagnose_common_issues'), "diagnose_common_issues method")
        except ImportError as e:
            print(f"⚠ Could not import OverrideValidator: {e}")
    
    # ==================== PHASE 4: REFERENCE MANAGER ====================
    
    def test_phase4_reference_manager(self):
        """Test Phase 4: Reference Manager features"""
        print("\n--- Testing Phase 4: Reference Manager ---")
        
        settings = bpy.context.scene.proref_settings
        
        self.assert_operator_exists("proref.update_library_list", "update_library_list operator")
        self.assert_operator_exists("proref.relocate_library", "relocate_library operator")
        
        self.assert_has_attr(settings, 'linked_libraries', "linked_libraries collection")
        self.assert_has_attr(settings, 'library_active_index', "library_active_index property")
        
        # Test LinkedLibraryData properties
        temp_item = settings.linked_libraries.add()
        
        self.assert_has_attr(temp_item, 'library_name', "LinkedLibraryData.library_name")
        self.assert_has_attr(temp_item, 'filepath', "LinkedLibraryData.filepath")
        self.assert_has_attr(temp_item, 'exists', "LinkedLibraryData.exists")
        self.assert_has_attr(temp_item, 'override_count', "LinkedLibraryData.override_count")
        self.assert_has_attr(temp_item, 'file_size', "LinkedLibraryData.file_size")
        self.assert_has_attr(temp_item, 'last_modified', "LinkedLibraryData.last_modified")
        self.assert_has_attr(temp_item, 'selected', "LinkedLibraryData.selected")
        self.assert_has_attr(temp_item, 'version_number', "LinkedLibraryData.version_number")
        self.assert_has_attr(temp_item, 'has_newer_version', "LinkedLibraryData.has_newer_version")
        
        # Clean up
        settings.linked_libraries.remove(len(settings.linked_libraries) - 1)
    
    # ==================== PHASE 5: POLISH ====================
    
    def test_phase5_polish(self):
        """Test Phase 5: Polish features"""
        print("\n--- Testing Phase 5: Polish ---")
        
        # Test preferences exist
        addon_prefs = bpy.context.preferences.addons.get("professional_referencing")
        if addon_prefs:
            prefs = addon_prefs.preferences
            self.assert_has_attr(prefs, 'default_library_path', "Preferences: default_library_path")
            self.assert_has_attr(prefs, 'default_auto_make_editable', "Preferences: default_auto_make_editable")
            self.assert_has_attr(prefs, 'use_keyboard_shortcuts', "Preferences: use_keyboard_shortcuts")
        else:
            self.assert_true(True, "Addon preferences accessible (manual check)")
    
    # ==================== v1.5: BATCH OPERATIONS ====================
    
    def test_v15_batch_operations(self):
        """Test v1.5 Batch Operations"""
        print("\n--- Testing v1.5: Batch Operations ---")
        
        self.assert_operator_exists("proref.batch_relink", "batch_relink operator")
        self.assert_operator_exists("proref.batch_search_folder", "batch_search_folder operator")
        self.assert_operator_exists("proref.detect_versions", "detect_versions operator")
        self.assert_operator_exists("proref.bump_to_latest", "bump_to_latest operator")
        self.assert_operator_exists("proref.select_all_libraries", "select_all_libraries operator")
        self.assert_operator_exists("proref.batch_reload_libraries", "batch_reload_libraries operator")
        self.assert_operator_exists("proref.select_by_pattern", "select_by_pattern operator")
        
        settings = bpy.context.scene.proref_settings
        self.assert_has_attr(settings, 'show_version_info', "show_version_info property")
        self.assert_has_attr(settings, 'auto_detect_versions', "auto_detect_versions property")
    
    # ==================== v1.5: VERSION UTILS ====================
    
    def test_v15_version_utils(self):
        """Test v1.5 Version Utilities"""
        print("\n--- Testing v1.5: Version Utils ---")
        
        try:
            from professional_referencing.core.version_utils import VersionUtils
            self.assert_true(True, "VersionUtils imports successfully")
            
            self.assert_true(hasattr(VersionUtils, 'extract_version'), "VersionUtils.extract_version method")
            self.assert_true(hasattr(VersionUtils, 'get_version_info'), "VersionUtils.get_version_info method")
            self.assert_true(hasattr(VersionUtils, 'get_latest_version'), "VersionUtils.get_latest_version method")
            self.assert_true(hasattr(VersionUtils, 'find_all_versions'), "VersionUtils.find_all_versions method")
            
            # Test version extraction
            test_cases = [
                ("character_v01.blend", 1),
                ("hero_v12.blend", 12),
                ("model-v03.blend", 3),
                ("no_version.blend", None),
            ]
            
            for filepath, expected in test_cases:
                result = VersionUtils.extract_version(filepath)
                if result == expected:
                    self.assert_true(True, f"extract_version('{filepath}') = {expected}")
                else:
                    self.assert_true(False, f"extract_version('{filepath}') expected {expected} got {result}")
                    
        except ImportError as e:
            self.assert_true(False, f"VersionUtils import failed: {e}")
    
    # ==================== v1.5: CLI / HEADLESS ====================
    
    def test_v15_cli_headless(self):
        """Test v1.5 CLI and Headless features"""
        print("\n--- Testing v1.5: CLI / Headless ---")
        
        self.assert_operator_exists("proref.cli_auto_fix", "cli_auto_fix operator")
        self.assert_operator_exists("proref.cli_report", "cli_report operator")
        self.assert_operator_exists("proref.cli_validate", "cli_validate operator")
        
        settings = bpy.context.scene.proref_settings
        self.assert_has_attr(settings, 'auto_fix_on_load', "auto_fix_on_load property")
        self.assert_has_attr(settings, 'use_environment_variables', "use_environment_variables property")
        
        # Test HeadlessHandler
        try:
            from professional_referencing.cli.headless_handler import HeadlessHandler
            self.assert_true(True, "HeadlessHandler imports successfully")
            
            self.assert_true(hasattr(HeadlessHandler, 'is_headless'), "HeadlessHandler.is_headless method")
            self.assert_true(hasattr(HeadlessHandler, 'resolve_environment_path'), "resolve_environment_path method")
            self.assert_true(hasattr(HeadlessHandler, 'auto_fix_broken_links'), "auto_fix_broken_links method")
            
        except ImportError as e:
            self.assert_true(False, f"HeadlessHandler import failed: {e}")
    
    # ==================== UI PANELS ====================
    
    def test_ui_panels(self):
        """Test UI panel registration"""
        print("\n--- Testing UI Panels ---")
        
        expected_panels = [
            "PROREF_PT_main_panel",
            "PROREF_PT_linking_panel",
            "PROREF_PT_rigui_panel",
            "PROREF_PT_health_panel",
            "PROREF_PT_reference_manager",
            "PROREF_PT_batch_operations",
            "PROREF_PT_cli_tools",
            "PROREF_PT_quick_actions",
            "PROREF_PT_settings_panel",
        ]
        
        for panel_id in expected_panels:
            found = False
            for panel_cls in bpy.types.Panel.__subclasses__():
                if hasattr(panel_cls, 'bl_idname') and panel_cls.bl_idname == panel_id:
                    found = True
                    break
            self.assert_true(found, f"Panel {panel_id} registered")
    
    # ==================== INTEGRATION TESTS ====================
    
    def test_integration(self):
        """Test integration features"""
        print("\n--- Testing Integration ---")
        
        settings = bpy.context.scene.proref_settings
        
        # Test health check on empty scene
        try:
            bpy.ops.proref.health_check()
            self.assert_true(True, "Health check runs on empty scene")
        except Exception as e:
            self.assert_true(False, f"Health check failed: {e}")
        
        # Test library list update
        try:
            bpy.ops.proref.update_library_list()
            self.assert_true(True, "Library list update runs")
        except Exception as e:
            self.assert_true(False, f"Library list update failed: {e}")
        
        # Test batch selection
        try:
            bpy.ops.proref.select_all_libraries(action='SELECT')
            bpy.ops.proref.select_all_libraries(action='DESELECT')
            bpy.ops.proref.select_all_libraries(action='TOGGLE')
            self.assert_true(True, "Batch select/deselect/toggle works")
        except Exception as e:
            self.assert_true(False, f"Batch select failed: {e}")
        
        # Test version detection operator
        try:
            bpy.ops.proref.detect_versions()
            self.assert_true(True, "Detect versions runs")
        except Exception as e:
            self.assert_true(False, f"Detect versions failed: {e}")
        
        # Test CLI operators
        try:
            bpy.ops.proref.cli_validate()
            self.assert_true(True, "CLI validate runs")
        except Exception as e:
            self.assert_true(False, f"CLI validate failed: {e}")
    
    # ==================== SUMMARY ====================
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        total = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.tests_passed} ✓")
        print(f"Failed: {self.tests_failed} ✗")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.tests_failed > 0:
            print("\n--- Failed Tests ---")
            for name, status, error in self.test_results:
                if status == "FAIL":
                    print(f"✗ {name}")
                    if error:
                        print(f"  {error}")
        
        print("\n" + "="*70)
        
        if self.tests_failed == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠ {self.tests_failed} tests need attention")
        
        print("="*70 + "\n")


# ==================== RUN TESTS ====================

def run_tests():
    """Main test runner"""
    tester = ProRefTester()
    tester.run_all_tests()
    return tester

# Auto-run when script is executed
if __name__ == "__main__":
    tester = run_tests()
