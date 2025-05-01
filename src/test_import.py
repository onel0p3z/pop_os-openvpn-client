#!/usr/bin/env python3

import subprocess
import os
import sys
import tempfile

def test_openvpn3_cli():
    """Test basic openvpn3 CLI functionality"""
    print("Testing openvpn3 CLI access...")
    try:
        # openvpn3 doesn't have a --version flag, use help instead
        result = subprocess.run(["openvpn3", "version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        print(f"openvpn3 version output: {result.stdout.strip()}")
        if result.returncode != 0:
            print(f"Error running openvpn3: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception testing openvpn3 CLI: {str(e)}")
        return False

def test_configs_list():
    """Test listing of openvpn configs"""
    print("Testing openvpn3 configs-list...")
    try:
        result = subprocess.run(["openvpn3", "configs-list"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        print(f"Configs list output:\n{result.stdout.strip()}")
        if result.returncode != 0:
            print(f"Error listing configs: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception listing configs: {str(e)}")
        return False

def create_test_ovpn():
    """Create a minimal test .ovpn file"""
    print("Creating test .ovpn file...")
    with tempfile.NamedTemporaryFile(suffix='.ovpn', delete=False) as tf:
        tf.write(b"""# Test OpenVPN config
client
dev tun
proto udp
remote test.example.com 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-GCM
verb 3
""")
        return tf.name

def test_config_import(ovpn_path):
    """Test importing a config file"""
    print(f"Testing openvpn3 config-import with {ovpn_path}...")
    try:
        # First check for correct command syntax
        result = subprocess.run(["openvpn3", "config-import", "--help"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        print(f"Import help output:\n{result.stdout.strip()}")
        
        # Now try the actual import
        result = subprocess.run(["openvpn3", "config-import", "--config", ovpn_path], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        print(f"Import output:\n{result.stdout.strip()}")
        
        if result.returncode != 0:
            print(f"Error importing config: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception importing config: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== OpenVPN3 Client Testing ===")
    
    if not test_openvpn3_cli():
        print("Failed to access openvpn3 CLI")
        sys.exit(1)
    
    test_configs_list()
    
    test_ovpn = create_test_ovpn()
    print(f"Created test OVPN at: {test_ovpn}")
    
    if test_config_import(test_ovpn):
        print("Successfully imported test configuration")
    else:
        print("Failed to import test configuration")
    
    # Clean up
    try:
        os.unlink(test_ovpn)
        print(f"Cleaned up test file: {test_ovpn}")
    except:
        pass