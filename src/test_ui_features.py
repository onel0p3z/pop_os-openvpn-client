#!/usr/bin/env python3

import unittest
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import subprocess
import os
import tempfile
from pathlib import Path

# Import the main application
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.openvpn_client import OpenVPNClient

class MockSubprocess:
    """Mock subprocess to simulate openvpn3 responses for testing"""
    
    @staticmethod
    def run(cmd, stdout=None, stderr=None, text=None):
        """Mock the subprocess.run function"""
        
        class Result:
            def __init__(self, returncode, stdout, stderr):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr
        
        # Store the command for inspection if needed
        MockSubprocess.last_command = cmd
        
        # Mock configs-list command
        if cmd[0] == "openvpn3" and cmd[1] == "configs-list":
            output = """
/net/openvpn/v3/configuration/1234567890abcdef
    name: Test Profile 1
    created: Thu Feb 28 12:00:00 2025
    import_path: /path/to/test1.ovpn
    
/net/openvpn/v3/configuration/abcdef1234567890
    name: Test Profile 2
    created: Thu Feb 28 13:00:00 2025
    import_path: /path/to/test2.ovpn
"""
            return Result(0, output, "")
        
        # Mock config-import command
        elif cmd[0] == "openvpn3" and cmd[1] == "config-import":
            output = """
Configuration imported. Configuration path: /net/openvpn/v3/configuration/1234567890abcdef
"""
            return Result(0, output, "")
        
        # Default response for unhandled commands
        return Result(1, "", "Command not supported in mock")
    
    # Static variable to store the last command
    last_command = None


class TestOpenVPNClientUI(unittest.TestCase):
    
    def setUp(self):
        """Set up the test environment"""
        self.original_subprocess_run = subprocess.run
        subprocess.run = MockSubprocess.run
        
        self.app = OpenVPNClient()
        # We need to call on_activate manually for testing
        self.app.on_activate(self.app)
        
        # Create a temporary .ovpn file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".ovpn", delete=False)
        self.temp_file.write(b"# Test OpenVPN config\nremote test.example.com 1194 udp")
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up after tests"""
        subprocess.run = self.original_subprocess_run
        if hasattr(self, 'app') and hasattr(self.app, 'window'):
            self.app.window.destroy()
        
        # Remove temporary file
        if hasattr(self, 'temp_file'):
            os.unlink(self.temp_file.name)
    
    def test_refresh_button_exists(self):
        """Test that the refresh button exists in the header bar"""
        header_bar = self.app.window.get_titlebar()
        refresh_button = None
        
        # Check all children of header bar for the refresh button
        for child in header_bar.get_children():
            if isinstance(child, Gtk.Button) and child.get_tooltip_text() == "Refresh VPN Profiles":
                refresh_button = child
                break
        
        self.assertIsNotNone(refresh_button, "Refresh button not found in header bar")
    
    def test_load_profiles_with_details(self):
        """Test that profiles are loaded with proper details"""
        # Trigger profile loading
        self.app.load_profiles()
        
        # Check that profiles were loaded
        self.assertEqual(len(self.app.vpn_profiles), 2, "Should have loaded 2 profiles")
        
        # Check first profile details
        profile1 = self.app.vpn_profiles[0]
        self.assertEqual(profile1.get("display_name"), "Test Profile 1", "First profile should have correct name")
        self.assertEqual(profile1.get("created"), "Thu Feb 28 12:00:00 2025", "First profile should have creation date")
        self.assertEqual(profile1.get("config_path"), "/net/openvpn/v3/configuration/1234567890abcdef", 
                        "First profile should have correct config path")
    
    def test_profile_listbox_displays_details(self):
        """Test that the listbox displays profile details correctly"""
        # Force loading profiles
        self.app.load_profiles()
        
        # Check number of rows
        rows = self.app.profiles_listbox.get_children()
        self.assertEqual(len(rows), 2, "Listbox should have 2 rows")
        
        # Check first row content (profile name should be in bold)
        row1 = rows[0]
        vbox = row1.get_child()
        hbox = vbox.get_children()[0]  # First child is the hbox for name
        name_label = hbox.get_children()[0]  # First child of hbox is the name label
        
        # Get the label text (removing markup)
        label_text = name_label.get_label()
        self.assertTrue("<b>Test Profile 1</b>" in label_text, 
                        f"Profile name should be bold: {label_text}")
    
    def test_import_dialog_customization(self):
        """Test that import dialog allows name customization"""
        # Prepare a simple test for the import profile feature with name customization
        
        # Override the dialog and entry functionality to simulate user input
        def mock_dialog_run(self):
            return Gtk.ResponseType.OK
        
        def mock_entry_get_text(self):
            return "Custom Name"
        
        # Store the original methods
        original_dialog_run = Gtk.Dialog.run
        original_entry_get_text = Gtk.Entry.get_text
        
        # Apply our mocks
        Gtk.Dialog.run = mock_dialog_run
        Gtk.Entry.get_text = mock_entry_get_text
        
        # Reset the last command
        MockSubprocess.last_command = None
        
        try:
            # Call the import method
            self.app.import_profile(self.temp_file.name)
            
            # Verify the command contained the --name parameter with our custom name
            self.assertIsNotNone(MockSubprocess.last_command, "Should have captured a command")
            self.assertEqual(MockSubprocess.last_command[0], "openvpn3", "Should call openvpn3")
            self.assertEqual(MockSubprocess.last_command[1], "config-import", "Should call config-import")
            self.assertIn("--name", MockSubprocess.last_command, "Should include the --name parameter")
            
            # Check that the custom name is used
            name_index = MockSubprocess.last_command.index("--name")
            self.assertEqual(MockSubprocess.last_command[name_index + 1], "Custom Name", 
                           "Should use the custom name from the dialog")
        finally:
            # Restore the original methods
            Gtk.Dialog.run = original_dialog_run
            Gtk.Entry.get_text = original_entry_get_text


if __name__ == "__main__":
    unittest.main()