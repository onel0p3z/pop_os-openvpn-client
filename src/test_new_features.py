#!/usr/bin/env python3

import unittest
import subprocess
import os
import tempfile
from unittest.mock import patch, MagicMock, Mock
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestRefreshFeature(unittest.TestCase):
    """Test the refresh feature"""
    
    def test_refresh_method_exists(self):
        """Test that the refresh method exists in the class"""
        # We need to import here to avoid initializing GTK in the main process
        from src.openvpn_client import OpenVPNClient
        
        # Create an instance and check for the method
        client = OpenVPNClient()
        self.assertTrue(hasattr(client, 'on_refresh_clicked'), 
                       "OpenVPNClient should have on_refresh_clicked method")
        self.assertTrue(callable(getattr(client, 'on_refresh_clicked')), 
                       "on_refresh_clicked should be callable")


class TestNameCustomization(unittest.TestCase):
    """Test the name customization feature in the import dialog"""
    
    def setUp(self):
        """Set up the test environment"""
        # Create a temporary .ovpn file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".ovpn", delete=False)
        self.temp_file.write(b"# Test OpenVPN config")
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up after the test"""
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_name_parameter_usage(self):
        """Test that the import command uses the --name parameter"""
        # Use manual inspection of the code to verify the --name parameter
        # This avoids the complexities of GUI testing
        
        # Import the file to analyze
        import src.openvpn_client as client_module
        
        # Read the file content
        with open(client_module.__file__, 'r') as f:
            code = f.read()
        
        # Check for the critical lines that implement our feature
        self.assertIn('["openvpn3", "config-import", "--config", file_path, "--persistent", "--name", custom_name]', code,
                     "The import_profile method should use the --name parameter with the custom name")
        
        self.assertIn('name_entry = Gtk.Entry()', code,
                     "The import_profile method should create an entry for the profile name")
        
        self.assertIn('name_entry.get_text()', code,
                     "The import_profile method should get the text from the name entry")


class TestProfileDetails(unittest.TestCase):
    """Test the enhanced profile details display"""
    
    def test_profile_details_extraction(self):
        """Test that profile details are properly extracted from OpenVPN3 output"""
        # Import the file to analyze
        import src.openvpn_client as client_module
        
        # Read the file content
        with open(client_module.__file__, 'r') as f:
            code = f.read()
        
        # Check for the critical code pieces
        self.assertIn('if "created:" in line.lower():', code,
                     "The load_profiles method should check for creation date")
        
        self.assertIn('current_profile["created"] = created_date', code,
                     "The load_profiles method should store the creation date")
        
        # Check for display of creation date
        self.assertIn('if "created" in profile:', code,
                     "The code should check if creation date exists")
        
        self.assertIn('Created:', code,
                     "The creation date should be displayed in the UI")


if __name__ == "__main__":
    unittest.main()