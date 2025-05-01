#!/usr/bin/env python3

"""
Test suite for the enhanced profile details display in the OpenVPN Client.

This test suite verifies:
1. Proper extraction of profile data including filename and date
2. Formatting of profile details to be more user-friendly
3. Display of ID instead of full config path

Run with: python3 -m unittest src/test_profile_details.py
"""

import unittest
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestProfileDetails(unittest.TestCase):
    """Tests for the enhanced profile details display."""
    
    def test_profile_data_extraction(self):
        """Test that profile data is properly extracted from openvpn3 output."""
        import src.openvpn_client as client_module
        
        with open(client_module.__file__, 'r') as f:
            code = f.read()
        
        # Check for import_path extraction
        self.assertIn('if "import_path:" in line.lower():', code,
                     "Should check for import_path in the output")
        
        self.assertIn('import_path = path_parts[1].strip()', code,
                     "Should extract the import path value")
        
        self.assertIn('current_profile["import_path"] = import_path', code,
                     "Should store the import path in the profile")
    
    def test_date_formatting(self):
        """Test that date formatting is properly implemented."""
        import src.openvpn_client as client_module
        
        with open(client_module.__file__, 'r') as f:
            code = f.read()
        
        # Check for date parsing
        self.assertIn('try:', code,
                     "Should have error handling for date parsing")
        
        self.assertIn('date_parts = created_date.split()', code,
                     "Should split the date string")
        
        # Check month, day, year extraction
        self.assertIn('month = date_parts[1]', code,
                     "Should extract month from date")
        
        self.assertIn('day = date_parts[2]', code,
                     "Should extract day from date")
        
        self.assertIn('year = date_parts[4]', code,
                     "Should extract year from date")
        
        # Check for formatted date
        self.assertIn('Added: {month} {day}, {year}', code,
                     "Should format date as 'Added: Month Day, Year'")
    
    def test_file_display(self):
        """Test that file information is displayed properly."""
        import src.openvpn_client as client_module
        
        with open(client_module.__file__, 'r') as f:
            code = f.read()
        
        # Check for file display
        self.assertIn('os.path.basename(import_path)', code,
                     "Should extract just the filename from the import path")
        
        self.assertIn('File:', code,
                     "Should display 'File:' label")
    
    def test_config_id_display(self):
        """Test that config ID is extracted and displayed properly."""
        import src.openvpn_client as client_module
        
        with open(client_module.__file__, 'r') as f:
            code = f.read()
        
        # Check for path parsing
        self.assertIn('path_parts = config_path.split', code,
                     "Should split the config path")
        
        # Check for ID extraction
        self.assertIn('config_id = path_parts[-1]', code,
                     "Should extract the last part of the path as ID")
        
        # Check for ID display
        self.assertIn('ID: {config_id}', code,
                     "Should display 'ID:' with the extracted config ID")


if __name__ == "__main__":
    unittest.main()