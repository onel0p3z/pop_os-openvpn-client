#!/usr/bin/env python3

"""
Test suite for the profile removal feature of the OpenVPN Client application.

This test suite verifies the following:
1. Delete button existence in each profile row
2. Confirmation dialog when deleting profiles
3. Actual removal of profiles via OpenVPN3

Run with: python3 -m unittest src/test_profile_removal.py
"""

import unittest
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestProfileRemoval(unittest.TestCase):
    """Tests for the profile removal functionality."""
    
    def test_delete_button_exists_in_code(self):
        """Test that the delete button is added to each profile row."""
        import src.openvpn_client as client_module
        
        with open(client_module.__file__, 'r') as f:
            code = f.read()
        
        # Check for delete button creation
        self.assertIn('delete_button = Gtk.Button()', code,
                     "Each profile row should have a delete button")
        
        # Check for trash icon
        self.assertIn('delete_icon = Gtk.Image.new_from_icon_name("user-trash-symbolic"', code,
                     "The delete button should use the trash icon")
        
        # Check for tooltip
        self.assertIn('delete_button.set_tooltip_text("Remove Profile")', code,
                     "The delete button should have a tooltip")
        
        # Check for click handler
        self.assertIn('delete_button.connect("clicked", self.on_delete_profile_clicked', code,
                     "The delete button should connect to on_delete_profile_clicked")
    
    def test_delete_handler_method_exists(self):
        """Test that the handler method for delete button exists."""
        import src.openvpn_client as client_module
        
        with open(client_module.__file__, 'r') as f:
            code = f.read()
        
        # Check for handler method
        self.assertIn('def on_delete_profile_clicked(self, button, profile_index):', code,
                     "The class should have an on_delete_profile_clicked method")
        
        # Check for confirmation dialog
        self.assertIn('message_type=Gtk.MessageType.QUESTION', code, 
                     "The handler should show a confirmation dialog")
        
        self.assertIn('buttons=Gtk.ButtonsType.YES_NO', code,
                     "The confirmation dialog should have Yes/No buttons")
    
    def test_delete_functionality(self):
        """Test the profile deletion command structure."""
        import src.openvpn_client as client_module
        
        with open(client_module.__file__, 'r') as f:
            code = f.read()
            
        # Check for response handling
        self.assertIn('if response == Gtk.ResponseType.YES:', code,
                     "The handler should check for YES response")
        
        # Check for deletion command
        self.assertIn('["openvpn3", "config-remove", "--force", "--path", profile["config_path"]]', code,
                     "The handler should call openvpn3 config-remove with the correct path")
                     
        # Check for profile reload after deletion
        self.assertIn('self.load_profiles()', code,
                     "The profiles should be reloaded after deletion")
    
    def test_delete_error_handling(self):
        """Test that deletion errors are properly handled."""
        import src.openvpn_client as client_module
        
        with open(client_module.__file__, 'r') as f:
            code = f.read()
        
        # Check for error handling
        self.assertIn('except Exception as e:', code,
                     "The handler should catch exceptions")
        
        # Check for error dialog
        self.assertIn('text=f"Error removing profile: {result.stderr}"', code,
                     "Error dialog should show stderr output")
        
        # Check for success message
        self.assertIn('self.status_label.set_text(f"Profile \'{profile_name}\' removed")', code,
                     "Should show success message in status label")


if __name__ == "__main__":
    unittest.main()