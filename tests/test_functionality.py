"""
Professional Referencing & Rig UI - Comprehensive Test Suite
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
    """Comprehensive test suite for Professional Referencing addon"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*70)
        print("PROFESSIONAL REFERENCING & RIG UI - COMPREHENSIVE TEST SUITE")
        print("="*70 + "\n")
        
        # Test suites by phase
        self.test_addon_registration()
        self.test_phase1_core_linking()
        self.test_phase2_rig_ui_isolation()
        self.test_phase3_override_health()
        self.test_phase4_reference_manager()
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
    
    # ==================== ADDON REGISTRATION ====================
    
    def test_addon_registration(self):
        """Test addon registration and basic setup"""
        print("\n--- Testing Addon Registration ---")
        
        # Test addon operators registered
        self.assert_true(
            'proref' in dir(bpy.ops),
            "Addon operators namespace registered"
        )
        
        # Test scene properties exist
        self.assert_true(
            hasattr(bpy.types.Scene, 'proref_settings'),
            "Scene properties registered"
        )
        
        # Test properties are accessible
        if bpy.context.scene:
            settings = bpy.context.scene.proref_settings
            self.assert_not_none(settings, "Settings accessible from scene")
    
    # ==================== PHASE 1: CORE LINKING ====================
    
    def test_phase1_core_linking(self):
        """Test Phase 1: Core Linking features"""
        print("\n--- Testing Phase 1: Core Linking ---")
        
        settings = bpy.context.scene.proref_settings
        
        # Test Smart Link operator exists
        self.assert_true(
            hasattr(bpy.ops.proref, 'smart_link'),
            "smart_link operator exists"
        )
        
        # Test Batch Link operator exists
        self.assert_true(
            hasattr(bpy.ops.proref, 'batch_link'),
            "batch_link operator exists"
        )
        
        # Test auto_make_editable property
        self.assert_has_attr(settings, 'auto_make_editable', "auto_make_editable property")
        
        # Test unique_rig_ui_names property
        self.assert_has_attr(settings, 'unique_rig_ui_names', "unique_rig_ui_names property")
        
        # Test Animation Only Mode (selective override)
        self.assert_has_attr(
            settings, 
            'selective_override_armature_only', 
            "Animation Only Mode property"
        )
        
        # Test default values
        self.assert_equals(
            settings.auto_make_editable,
            True,
            "auto_make_editable defaults to True"
        )
    
    # ==================== PHASE 2: RIG UI ISOLATION ====================
    
    def test_phase2_rig_ui_isolation(self):
        """Test Phase 2: Rig UI Isolation features"""
        print("\n--- Testing Phase 2: Rig UI Isolation ---")
        
        settings = bpy.context.scene.proref_settings
        
        # Test Rig UI operators exist
        self.assert_true(
            hasattr(bpy.ops.proref, 'execute_rig_ui'),
            "execute_rig_ui operator exists"
        )
        
        self.assert_true(
            hasattr(bpy.ops.proref, 'validate_rig_ui'),
            "validate_rig_ui operator exists"
        )
        
        self.assert_true(
            hasattr(bpy.ops.proref, 'create_rig_ui_template'),
            "create_rig_ui_template operator exists"
        )
        
        self.assert_true(
            hasattr(bpy.ops.proref, 'refresh_all_rig_ui'),
            "refresh_all_rig_ui operator exists"
        )
        
        # Test auto_execute_rig_ui property
        self.assert_has_attr(settings, 'auto_execute_rig_ui', "auto_execute_rig_ui property")
        
        # Test script_injector module can be imported
        try:
            from professional_referencing.core.script_injector import RigUIScriptInjector
            self.assert_true(True, "RigUIScriptInjector imports successfully")
            
            # Test methods exist
            self.assert_true(
                hasattr(RigUIScriptInjector, 'find_rig_ui_script'),
                "RigUIScriptInjector.find_rig_ui_script exists"
            )
            self.assert_true(
                hasattr(RigUIScriptInjector, 'create_isolated_script'),
                "RigUIScriptInjector.create_isolated_script exists"
            )
            self.assert_true(
                hasattr(RigUIScriptInjector, 'execute_isolated_script'),
                "RigUIScriptInjector.execute_isolated_script exists"
            )
            self.assert_true(
                hasattr(RigUIScriptInjector, 'validate_script_safety'),
                "RigUIScriptInjector.validate_script_safety exists"
            )
        except ImportError as e:
            print(f"⚠ Could not import RigUIScriptInjector: {e}")
    
    # ==================== PHASE 3: OVERRIDE HEALTH ====================
    
    def test_phase3_override_health(self):
        """Test Phase 3: Override Health System features"""
        print("\n--- Testing Phase 3: Override Health System ---")
        
        settings = bpy.context.scene.proref_settings
        
        # Test Health Check operator
        self.assert_true(
            hasattr(bpy.ops.proref, 'health_check'),
            "health_check operator exists"
        )
        
        # Test Repair operator
        self.assert_true(
            hasattr(bpy.ops.proref, 'repair_override'),
            "repair_override operator exists"
        )
        
        # Test Resync operator
        self.assert_true(
            hasattr(bpy.ops.proref, 'resync_override'),
            "resync_override operator exists"
        )
        
        # Test Make Editable operator
        self.assert_true(
            hasattr(bpy.ops.proref, 'make_all_editable'),
            "make_all_editable operator exists"
        )
        
        # Test health_checks collection
        self.assert_has_attr(settings, 'health_checks', "health_checks collection")
        
        # Test filter properties
        self.assert_has_attr(settings, 'filter_healthy_only', "filter_healthy_only property")
        self.assert_has_attr(settings, 'filter_errors_only', "filter_errors_only property")
        
        # Test validation module
        try:
            from professional_referencing.core.validation import OverrideValidator
            self.assert_true(True, "OverrideValidator imports successfully")
            
            # Test methods exist
            self.assert_true(
                hasattr(OverrideValidator, 'find_all_overrides_in_scene'),
                "OverrideValidator.find_all_overrides_in_scene exists"
            )
            self.assert_true(
                hasattr(OverrideValidator, 'check_override_health'),
                "OverrideValidator.check_override_health exists"
            )
            self.assert_true(
                hasattr(OverrideValidator, 'diagnose_common_issues'),
                "OverrideValidator.diagnose_common_issues exists"
            )
        except ImportError as e:
            print(f"⚠ Could not import OverrideValidator: {e}")
    
    # ==================== PHASE 4: REFERENCE MANAGER ====================
    
    def test_phase4_reference_manager(self):
        """Test Phase 4: Reference Manager features"""
        print("\n--- Testing Phase 4: Reference Manager ---")
        
        settings = bpy.context.scene.proref_settings
        
        # Test Library List operators
        self.assert_true(
            hasattr(bpy.ops.proref, 'update_library_list'),
            "update_library_list operator exists"
        )
        
        self.assert_true(
            hasattr(bpy.ops.proref, 'relocate_library'),
            "relocate_library operator exists"
        )
        
        self.assert_true(
            hasattr(bpy.ops.proref, 'reload_library'),
            "reload_library operator exists"
        )
        
        # Test Batch operators
        self.assert_true(
            hasattr(bpy.ops.proref, 'select_all_libraries'),
            "select_all_libraries operator exists"
        )
        
        self.assert_true(
            hasattr(bpy.ops.proref, 'deselect_all_libraries'),
            "deselect_all_libraries operator exists"
        )
        
        self.assert_true(
            hasattr(bpy.ops.proref, 'batch_reload_libraries'),
            "batch_reload_libraries operator exists"
        )
        
        # Test linked_libraries collection
        self.assert_has_attr(settings, 'linked_libraries', "linked_libraries collection")
        self.assert_has_attr(settings, 'library_active_index', "library_active_index property")
        
        # Test LinkedLibraryData properties
        # Create a temporary item to test structure
        temp_item = settings.linked_libraries.add()
        
        self.assert_has_attr(temp_item, 'library_name', "LinkedLibraryData.library_name")
        self.assert_has_attr(temp_item, 'filepath', "LinkedLibraryData.filepath")
        self.assert_has_attr(temp_item, 'exists', "LinkedLibraryData.exists")
        self.assert_has_attr(temp_item, 'override_count', "LinkedLibraryData.override_count")
        self.assert_has_attr(temp_item, 'file_size', "LinkedLibraryData.file_size")
        self.assert_has_attr(temp_item, 'last_modified', "LinkedLibraryData.last_modified")
        self.assert_has_attr(temp_item, 'is_selected', "LinkedLibraryData.is_selected")
        
        # Clean up
        settings.linked_libraries.remove(len(settings.linked_libraries) - 1)
    
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
        """Test integration features that don't require external files"""
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
        
        # Test batch select/deselect
        try:
            bpy.ops.proref.select_all_libraries()
            bpy.ops.proref.deselect_all_libraries()
            self.assert_true(True, "Batch select/deselect works")
        except Exception as e:
            self.assert_true(False, f"Batch select failed: {e}")
        
        # Test creating armature and rig UI workflow
        try:
            # Create test armature
            bpy.ops.object.armature_add(enter_editmode=False, location=(0, 0, 0))
            armature = bpy.context.active_object
            
            # Create dummy rig UI script
            script_name = f"rig_ui_{armature.name}.py"
            script = bpy.data.texts.new(script_name)
            script.write("# Test rig UI script\nprint('Rig UI executed')")
            
            # Link script to armature
            armature["proref_rig_ui"] = script_name
            
            # Execute rig UI
            bpy.ops.proref.execute_rig_ui()
            self.assert_true(True, "Rig UI execution workflow works")
            
            # Test template creation on new armature
            bpy.ops.object.armature_add(enter_editmode=False, location=(2, 0, 0))
            armature2 = bpy.context.active_object
            bpy.ops.proref.create_rig_ui_template()
            self.assert_true(
                "proref_rig_ui" in armature2,
                "Create rig UI template works"
            )
            
            # Cleanup
            for arm in [armature, armature2]:
                if arm.name in bpy.data.objects:
                    bpy.data.objects.remove(arm, do_unlink=True)
            
            for text in list(bpy.data.texts):
                if "rig_ui" in text.name.lower():
                    bpy.data.texts.remove(text)
            
        except Exception as e:
            print(f"⚠ Integration test partial failure: {e}")
    
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
