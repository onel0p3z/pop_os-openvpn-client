# Pop!_OS OpenVPN GTK Client

[![made with claude code](https://img.shields.io/badge/made_by_claude_code_with_%E2%9D%A4%EF%B8%8F-orange)]()
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/onel0p3z)


A simple GTK-based graphical user interface for managing OpenVPN connections on Pop!_OS, built on top of the openvpn3 command-line tool.

I asked Claude Code to help me make this tool and it worked. I hope it helps you, too!

## Features

- Import OpenVPN configuration files (.ovpn) with custom naming
- List available VPN profiles with detailed information (filename, creation date, config ID)
- Connect to and disconnect from OpenVPN servers
- Remove VPN profiles with confirmation
- Monitor connection status
- Refresh VPN profiles when changes occur outside the application

## Requirements

- Pop!_OS (or any Linux with GTK 3)
- Python 3.6+
- PyGObject
- OpenVPN 3 Linux client

## Installation

### 1. Install OpenVPN 3 Linux client

Follow the installation instructions at the [OpenVPN 3 Linux client page](https://community.openvpn.net/openvpn/wiki/OpenVPN3Linux).

For Ubuntu/Pop!_OS (20.04 or newer):

```bash
# Add the OpenVPN repository
apt install apt-transport-https
curl -fsSL https://swupdate.openvpn.net/repos/openvpn-repo-pkg-key.pub | gpg --dearmor > /etc/apt/trusted.gpg.d/openvpn-repo-pkg-keyring.gpg
echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/openvpn-repo-pkg-keyring.gpg] https://swupdate.openvpn.net/apt focal main" > /etc/apt/sources.list.d/openvpn3.list

# Update and install
apt update
apt install openvpn3
```

### 2. Install Python dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Install the application

```bash
# Clone the repository
cd /usr/src
git clone https://github.com/onel0p3z/pop_os-openvpn-client.git
cd pop_os-openvpn-client

# Make the script executable
chmod +x src/openvpn_client.py

# Copy the desktop file (optional, for system-wide installation)
sudo cp resources/pop-openvpn-client.desktop /usr/share/applications/
# Edit the desktop file to point to the correct path
sudo sed -i "s|/path/to/openvpn_client.py|$(pwd)/src/openvpn_client.py|g" /usr/share/applications/pop-openvpn-client.desktop
```

## Usage

### Running from the terminal

```bash
python3 src/openvpn_client.py
```

### Importing a profile

1. Click the "Import Profile" button
2. Select an OpenVPN (.ovpn) configuration file
3. Review and customize the profile name in the dialog
4. Click OK to import the profile
5. Enter any required credentials when prompted

### Connecting to a VPN

1. Select a profile from the list
2. Click the "Connect" button
3. Enter any required credentials when prompted

### Disconnecting

1. Click the "Disconnect" button

### Removing a Profile

1. Find the profile you want to remove in the list
2. Click the trash icon (🗑️) on the right side of the profile row
3. Confirm the deletion in the dialog that appears

### Refreshing Profiles

If you make changes to your VPN profiles outside the application (for example, using the command line):

1. Click the refresh button (⟳) in the header bar to reload your profiles

## Troubleshooting

If you encounter issues with the OpenVPN 3 client, you can check its status and logs with:

```bash
openvpn3 sessions-list
openvpn3 log --session-path /net/openvpn/v3/sessions/[session-id]
```

### Testing OpenVPN3 Functionality

The application includes several test scripts to verify OpenVPN3 functionality:

#### Basic OpenVPN3 Testing

```bash
python3 src/test_import.py
```

This script:
1. Tests basic OpenVPN3 CLI access
2. Lists existing configuration profiles
3. Creates a test .ovpn file
4. Tests importing the configuration
5. Cleans up the test file

#### Testing Import of Specific Configuration File

```bash
python3 src/test_import_specific.py /path/to/your/config.ovpn
```

This script:
1. Lists existing configurations
2. Imports the specified .ovpn file
3. Lists configurations again to verify it was imported

#### Testing Connection to VPN

```bash
python3 src/test_connection.py
```

This script:
1. Lists available configurations
2. Attempts to connect to the most recently imported configuration
3. Checks the connection status
4. Disconnects from the VPN

You can also specify a particular configuration:

```bash
python3 src/test_connection.py /path/to/your/config.ovpn
```

### OpenVPN3 CLI Tips

When working with OpenVPN3, be aware of these important command line parameters:

- `openvpn3 configs-list` - Lists all imported configurations
- `openvpn3 config-import --config /path/to/file.ovpn --persistent` - Imports a configuration (must use `--config`)
- `openvpn3 session-start --config-path /net/openvpn/v3/configuration/[id]` - Connects to an imported configuration
- `openvpn3 session-stats --path /net/openvpn/v3/sessions/[id]` - Checks connection status
- `openvpn3 session-manage --disconnect --path /net/openvpn/v3/sessions/[id]` - Disconnects a VPN session

## License

[MIT License](LICENSE)