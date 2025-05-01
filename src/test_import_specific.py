#!/usr/bin/env python3

import subprocess
import sys

def test_specific_config_import(ovpn_path):
    """Test importing a specific config file"""
    print(f"Testing openvpn3 config-import with {ovpn_path}...")
    try:
        # First get existing configurations to compare after
        result_before = subprocess.run(["openvpn3", "configs-list"], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, 
                                     text=True)
        print(f"Configs before import:\n{result_before.stdout.strip()}")
        
        # Now try the actual import
        print("\nImporting the configuration file...")
        result = subprocess.run(["openvpn3", "config-import", "--config", ovpn_path, "--persistent"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        print(f"Import command output:\n{result.stdout.strip()}")
        
        if result.stderr:
            print(f"Import stderr:\n{result.stderr.strip()}")
        
        if result.returncode != 0:
            print(f"Error importing config, return code: {result.returncode}")
            return False
            
        # Get configurations after import
        result_after = subprocess.run(["openvpn3", "configs-list"], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True)
        print(f"\nConfigs after import:\n{result_after.stdout.strip()}")
        
        return True
    except Exception as e:
        print(f"Exception importing config: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Testing Import of Specific OpenVPN Profile ===")
    
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "test_connection_dummy_file.ovpn"
    
    print(f"Using configuration file: {config_path}")
    
    if test_specific_config_import(config_path):
        print("\nTest PASSED: Successfully imported the configuration")
    else:
        print("\nTest FAILED: Could not import the configuration")