#!/usr/bin/env python3

import subprocess
import sys
import time

def get_configs():
    """Get a list of available config profiles"""
    try:
        result = subprocess.run(["openvpn3", "configs-list"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        
        if result.returncode != 0:
            print(f"Error listing configs: {result.stderr}")
            return []
            
        configs = []
        lines = result.stdout.strip().split('\n')
        current_config = None
        config_path = None
        name = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Config path line
            if line.startswith("/net/openvpn/v3/configuration/"):
                if current_config:
                    configs.append(current_config)
                
                config_path = line
                current_config = {"config_path": config_path}
            
            # File path usually appears on the next line after date/usage info
            elif config_path and current_config and not "Name" in current_config:
                if not line.startswith("---") and len(line.split()) >= 1 and i > 0:
                    # Try to extract the actual file path which is usually the last item
                    parts = line.split()
                    if len(parts) >= 1:
                        file_path = parts[-1]  # Last part is usually the filename or path
                        current_config["name"] = file_path
        
        if current_config:
            configs.append(current_config)
            
        return configs
    except Exception as e:
        print(f"Exception listing configs: {str(e)}")
        return []

def test_connection(config):
    """Test connecting to a specific config"""
    if isinstance(config, dict):
        config_path = config.get("name")  # Use the name/path field
        config_id = config.get("config_path")  # Use the OpenVPN3 config path
    else:
        config_path = config
        config_id = None
        
    print(f"Testing connection to {config_path}...")
    try:
        print("Attempting to connect...")
        
        # Try using the config_path (which should be the file path)
        result = subprocess.run(
            ["openvpn3", "session-start", "--config", config_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"Connect command output:\n{result.stdout.strip()}")
        
        if result.stderr:
            print(f"Connect stderr:\n{result.stderr.strip()}")
        
        if result.returncode != 0:
            print(f"Error connecting with file path, return code: {result.returncode}")
            
            # If we have a config_id, try that instead
            if config_id:
                print(f"\nRetrying with config path: {config_id}")
                result = subprocess.run(
                    ["openvpn3", "session-start", "--config-path", config_id],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                print(f"Connect command output:\n{result.stdout.strip()}")
                
                if result.stderr:
                    print(f"Connect stderr:\n{result.stderr.strip()}")
                
                if result.returncode != 0:
                    print(f"Error connecting with config path, return code: {result.returncode}")
                    return False
            else:
                return False
            
        # Extract session path if available
        session_path = None
        for line in result.stdout.split('\n'):
            if "Session path:" in line:
                session_path = line.split("Session path:")[1].strip()
                break
                
        if not session_path:
            print("Could not extract session path from output")
            return False
            
        print(f"Connected successfully. Session path: {session_path}")
        
        # Check session status
        print("\nChecking session status...")
        time.sleep(2)  # Wait a moment for the connection to establish
        
        status_result = subprocess.run(
            ["openvpn3", "session-stats", "--path", session_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"Session status output:\n{status_result.stdout.strip()}")
        
        if status_result.stderr:
            print(f"Session status stderr:\n{status_result.stderr.strip()}")
        
        # Disconnect
        print("\nDisconnecting...")
        disconnect_result = subprocess.run(
            ["openvpn3", "session-manage", "--disconnect", "--path", session_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"Disconnect output:\n{disconnect_result.stdout.strip()}")
        
        if disconnect_result.stderr:
            print(f"Disconnect stderr:\n{disconnect_result.stderr.strip()}")
            
        return True
    except Exception as e:
        print(f"Exception during connection test: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Testing OpenVPN Connection ===")
    
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        print(f"Using specified config path: {config_path}")
        config = config_path
    else:
        # List available configs and use the first one
        configs = get_configs()
        if not configs:
            print("No OpenVPN configurations found")
            sys.exit(1)
            
        print("Available configurations:")
        for i, config in enumerate(configs):
            print(f"{i+1}. {config.get('name', 'Unknown')} - {config.get('config_path', 'Unknown')}")
            
        # Use the most recently imported config (usually the first one)
        config = configs[0]
        print(f"\nUsing most recent config: {config.get('name', 'Unknown')}")
    
    if test_connection(config):
        print("\nTest PASSED: Successfully tested connection")
    else:
        print("\nTest FAILED: Could not complete connection test")