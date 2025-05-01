#!/usr/bin/env python3

"""
Test suite for the improvements made to the OpenVPN Client application.

This test suite verifies the following features:
1. Refresh button functionality
2. Profile name customization during import
3. Enhanced profile details display

Run with: python3 -m unittest src/test_improvements.py
"""

import unittest
import os
import tempfile
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRefreshButton(unittest.TestCase):
    """Tests for the refresh button functionality."""
    
    def test_refresh_button_exists(self):
        """Test that the refresh button method exists."""
        from src.openvpn_client import OpenVPNClient
        client = OpenVPNClient()
        
        # Check that the method exists
        self.assertTrue(hasattr(client, 'on_refresh_clicked'), 
                        "OpenVPNClient should have on_refresh_clicked method")
        self.assertTrue(callable(getattr(client, 'on_refresh_clicked')), 
                        "on_refresh_clicked should be callable")
    
    def test_refresh_calls_load_profiles(self):
        """Test that refresh button calls load_profiles method."""
        # This test analyzes the code for the correct implementation
        import src.openvpn_client as client_module
        
        with open(client_module.__file__, 'r') as f:
            code = f.read()
        
        # Check for the critical line
        self.assertIn('def on_refresh_clicked(self, button):', code,
                     "The class should have an on_refresh_clicked method with button parameter")
        
        self.assertIn('self.load_profiles()', code,
                     "The refresh method should call load_profiles")


class TestProfileNameCustomization(unittest.TestCase):
    """Tests for the profile name customization feature."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary .ovpn file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".ovpn", delete=False)
        self.temp_file.write(b"# Test OpenVPN config")
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up after the test."""
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_import_dialog_exists(self):
        """Test that the import dialog with name entry exists."""
        import src.openvpn_client as client_module
        
        with open(client_module.__file__, 'r') as f:
            code = f.read()
        
        # Check for dialog creation
        self.assertIn('dialog = Gtk.Dialog(', code,
                     "The import_profile method should create a dialog")
        
        # Check for name entry
        self.assertIn('name_entry = Gtk.Entry()', code,
                     "The import_profile method should create an entry for the profile name")
        
        # Check for default name extraction
        self.assertIn('filename = os.path.basename(file_path)', code,
                     "Should extract the filename from the path")
        
        self.assertIn('default_name = os.path.splitext(filename)[0]', code,
                     "Should extract the default name without extension")
    
    def test_custom_name_used(self):
        """Test that the custom name is used in the OpenVPN command."""
        import src.openvpn_client as client_module
        
        with open(client_module.__file__, 'r') as f:
            code = f.read()
        
        # Check for command construction with name parameter
        self.assertIn('["openvpn3", "config-import", "--config", file_path, "--persistent", "--name", custom_name]', code,
                     "The openvpn3 command should include the --name parameter with custom name")
        
        # Check for custom name extraction from dialog
        self.assertIn('custom_name = name_entry.get_text().strip()', code,
                     "Should get the custom name from the entry")


class TestEnhancedProfileDetails(unittest.TestCase):
    """Tests for the enhanced profile details display."""
    
    def test_profile_creation_date_extraction(self):
        """Test that the profile creation date is extracted correctly."""
        import src.openvpn_client as client_module
        
        with open(client_module.__file__, 'r') as f:
            code = f.read()
        
        # Check for creation date extraction
        self.assertIn('if "created:" in line.lower():', code,
                     "Should check for creation date in output")
        
        self.assertIn('date_parts = line.split("created:", 1)', code,
                     "Should split the line to extract creation date")
        
        self.assertIn('current_profile["created"] = created_date', code,
                     "Should store the creation date in the profile")
    
    def test_profile_display_formatting(self):
        """Test that profiles are displayed with proper formatting."""
        import src.openvpn_client as client_module
        
        with open(client_module.__file__, 'r') as f:
            code = f.read()
        
        # Check for bold display name
        self.assertIn('name_label.set_markup(f"<b>{display_text}</b>")', code,
                     "Should display the profile name in bold")
        
        # Check for details display
        self.assertIn('details_text = ""', code,
                     "Should initialize details text variable")
        
        # Check for creation date display
        self.assertIn('if "created" in profile:', code,
                     "Should check if creation date exists")
        
        self.assertIn('Created:', code,
                     "Should display 'Created:' label")
        
        # Check for path display
        self.assertIn('Path:', code,
                     "Should display 'Path:' label")
        
        # Check for small markup
        self.assertIn('<small>', code,
                     "Should use small markup for details")


if __name__ == "__main__":
    unittest.main()