#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio
import subprocess
import os
import json
from pathlib import Path

class OpenVPNClient(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.pop_os.openvpn_client",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)
        self.vpn_profiles = []
        self.active_connection = None

    def on_activate(self, app):
        self.window = Gtk.ApplicationWindow(application=app, title="OpenVPN Client")
        self.window.set_default_size(600, 400)
        self.window.set_border_width(10)

        # Create a header bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title("OpenVPN Client")
        self.window.set_titlebar(header)

        # Add button to import profile
        import_button = Gtk.Button(label="Import Profile")
        import_button.connect("clicked", self.on_import_clicked)
        header.pack_start(import_button)
        
        # Add refresh button with icon
        refresh_button = Gtk.Button()
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        refresh_button.set_image(refresh_icon)
        refresh_button.set_tooltip_text("Refresh VPN Profiles")
        refresh_button.connect("clicked", self.on_refresh_clicked)
        header.pack_end(refresh_button)

        # Create a box for the main content
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.window.add(main_box)

        # Profiles section
        profiles_frame = Gtk.Frame(label="VPN Profiles")
        main_box.pack_start(profiles_frame, True, True, 0)

        profiles_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        profiles_box.set_border_width(10)
        profiles_frame.add(profiles_box)

        # Create ScrolledWindow for profiles
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        profiles_box.pack_start(scrolled, True, True, 0)

        # Create a list box for profiles
        self.profiles_listbox = Gtk.ListBox()
        self.profiles_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.profiles_listbox.connect("row-selected", self.on_profile_selected)
        scrolled.add(self.profiles_listbox)

        # Status section
        status_frame = Gtk.Frame(label="Connection Status")
        main_box.pack_start(status_frame, False, True, 0)

        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        status_box.set_border_width(10)
        status_frame.add(status_box)

        self.status_label = Gtk.Label(label="Not connected")
        status_box.pack_start(self.status_label, False, False, 0)

        # Action buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        main_box.pack_start(button_box, False, False, 0)

        self.connect_button = Gtk.Button(label="Connect")
        self.connect_button.connect("clicked", self.on_connect_clicked)
        self.connect_button.set_sensitive(False)
        button_box.pack_start(self.connect_button, True, True, 0)

        self.disconnect_button = Gtk.Button(label="Disconnect")
        self.disconnect_button.connect("clicked", self.on_disconnect_clicked)
        self.disconnect_button.set_sensitive(False)
        button_box.pack_start(self.disconnect_button, True, True, 0)

        # Load profiles
        self.load_profiles()

        self.window.show_all()

    def on_refresh_clicked(self, button):
        self.load_profiles()
        
    def load_profiles(self):
        # Clear current list
        for child in self.profiles_listbox.get_children():
            self.profiles_listbox.remove(child)

        self.vpn_profiles = []

        try:
            # Get profiles from openvpn3
            result = subprocess.run(["openvpn3", "configs-list"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                current_profile = None
                config_path = None
                
                for i, line in enumerate(lines):
                    line = line.strip()
                    
                    # Config path line (always starts with /net/openvpn/v3/configuration/)
                    if line.startswith("/net/openvpn/v3/configuration/"):
                        if current_profile:
                            self.vpn_profiles.append(current_profile)
                        
                        # Save the config path and initialize new profile
                        config_path = line
                        current_profile = {
                            "config_path": config_path,
                            "name": "Unknown Profile"
                        }
                    
                    # The file path/name appears on a line after the config path
                    elif current_profile and config_path and not line.startswith("--") and i > 0:
                        # Try to extract useful information from the line
                        parts = line.split()
                        
                        # Extract profile name
                        if "name:" in line.lower():
                            name_parts = line.split("name:", 1)
                            if len(name_parts) > 1:
                                profile_name = name_parts[1].strip()
                                current_profile["display_name"] = profile_name
                        
                        # Extract file path if available and name isn't set
                        elif not "display_name" in current_profile and len(parts) >= 1:
                            file_path = parts[-1]
                            current_profile["file_path"] = file_path
                            current_profile["import_path"] = file_path  # Store import path for display
                            
                            # Extract a user-friendly name from the file path
                            # Use the filename portion only, without extension
                            import os.path
                            filename = os.path.basename(file_path)
                            display_name = os.path.splitext(filename)[0]
                            current_profile["display_name"] = display_name
                        
                        # Extract creation date if available
                        if "created:" in line.lower():
                            date_parts = line.split("created:", 1)
                            if len(date_parts) > 1:
                                created_date = date_parts[1].strip()
                                current_profile["created"] = created_date
                        
                        # Extract import path if available
                        if "import_path:" in line.lower():
                            path_parts = line.split("import_path:", 1)
                            if len(path_parts) > 1:
                                import_path = path_parts[1].strip()
                                current_profile["import_path"] = import_path
                
                # Add the final profile if it exists
                if current_profile:
                    self.vpn_profiles.append(current_profile)
            
            # Add profiles to the listbox
            for profile in self.vpn_profiles:
                row = Gtk.ListBoxRow()
                vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                row.add(vbox)
                
                # Create a main hbox for the first line
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                vbox.pack_start(hbox, True, True, 0)
                
                # Create a label with the display name or fallback to file path
                display_text = profile.get("display_name", 
                               profile.get("file_path", 
                               profile.get("name", "Unknown Profile")))
                
                name_label = Gtk.Label()
                name_label.set_markup(f"<b>{display_text}</b>")
                name_label.set_xalign(0)
                hbox.pack_start(name_label, True, True, 0)
                
                # Add second line with additional details
                details_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                vbox.pack_start(details_box, True, True, 0)
                
                # Create a string with all the profile details
                details_text = ""
                
                # Add server/endpoint information if available in the profile
                if "import_path" in profile:
                    import_path = profile.get("import_path", "")
                    details_text += f"File: {os.path.basename(import_path)} | "
                
                # Add creation date if available
                if "created" in profile:
                    # Format: "Created: Thu Feb 28 12:00:00 2025" -> "Added: Feb 28, 2025"
                    created_date = profile["created"]
                    try:
                        # Try to parse and reformat the date to be more user-friendly
                        import datetime
                        date_parts = created_date.split()
                        if len(date_parts) >= 4:
                            month = date_parts[1]
                            day = date_parts[2]
                            year = date_parts[4]
                            details_text += f"Added: {month} {day}, {year} | "
                    except:
                        # If parsing fails, use the original date
                        details_text += f"Added: {created_date} | "
                
                # Add config path (truncated and more user-friendly)
                config_path = profile.get("config_path", "")
                if config_path:
                    # Extract just the ID portion of the path
                    path_parts = config_path.split('/')
                    if len(path_parts) > 0:
                        config_id = path_parts[-1]
                        details_text += f"ID: {config_id}"
                    else:
                        # Fallback to truncated path
                        if len(config_path) > 30:
                            config_path = config_path[:27] + "..."
                        details_text += f"Path: {config_path}"
                
                # Add the details label
                details_label = Gtk.Label()
                details_label.set_markup(f"<small>{details_text}</small>")
                details_label.set_xalign(0)
                details_box.pack_start(details_label, True, True, 0)
                
                # Add a delete button on the right side of the main row
                delete_button = Gtk.Button()
                delete_icon = Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
                delete_button.set_image(delete_icon)
                delete_button.set_tooltip_text("Remove Profile")
                delete_button.set_relief(Gtk.ReliefStyle.NONE)  # Make button less prominent
                
                # Store the profile index in the button
                delete_button.connect("clicked", self.on_delete_profile_clicked, len(self.vpn_profiles) - 1)
                
                hbox.pack_end(delete_button, False, False, 0)
                
                self.profiles_listbox.add(row)
            
            self.profiles_listbox.show_all()
            
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self.window,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"Error loading profiles: {str(e)}"
            )
            dialog.run()
            dialog.destroy()

    def on_profile_selected(self, listbox, row):
        if row is not None:
            self.connect_button.set_sensitive(True)
            self.selected_profile_index = row.get_index()
        else:
            self.connect_button.set_sensitive(False)
            self.selected_profile_index = None

    def on_import_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Import OpenVPN Profile",
            parent=self.window,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )

        # Add filters for .ovpn files
        filter_ovpn = Gtk.FileFilter()
        filter_ovpn.set_name("OpenVPN Files")
        filter_ovpn.add_pattern("*.ovpn")
        dialog.add_filter(filter_ovpn)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            dialog.destroy()
            self.import_profile(file_path)
        else:
            dialog.destroy()

    def import_profile(self, file_path):
        try:
            # Extract default profile name from file path (without extension)
            import os.path
            filename = os.path.basename(file_path)
            default_name = os.path.splitext(filename)[0]
            
            # Show dialog to confirm/customize profile name
            dialog = Gtk.Dialog(
                title="Import Profile",
                transient_for=self.window,
                flags=0
            )
            dialog.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK, Gtk.ResponseType.OK
            )
            dialog.set_default_response(Gtk.ResponseType.OK)
            
            # Create a box for the dialog content
            content_area = dialog.get_content_area()
            content_area.set_border_width(10)
            content_area.set_spacing(10)
            
            # Add label and entry for profile name
            name_label = Gtk.Label(label="Profile Name:")
            name_label.set_xalign(0)
            content_area.add(name_label)
            
            name_entry = Gtk.Entry()
            name_entry.set_text(default_name)
            name_entry.set_activates_default(True)
            content_area.add(name_entry)
            
            # Show file path as information
            path_label = Gtk.Label()
            path_label.set_markup(f"<small>File: {file_path}</small>")
            path_label.set_xalign(0)
            content_area.add(path_label)
            
            dialog.show_all()
            response = dialog.run()
            
            if response == Gtk.ResponseType.OK:
                custom_name = name_entry.get_text().strip()
                if not custom_name:
                    custom_name = default_name
                
                dialog.destroy()
                
                # Import the profile with OpenVPN3
                result = subprocess.run(
                    ["openvpn3", "config-import", "--config", file_path, "--persistent", "--name", custom_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if result.returncode == 0:
                    # Try to extract the configuration path from the output
                    config_path = None
                    for line in result.stdout.split('\n'):
                        if "Configuration path:" in line:
                            config_path = line.split("Configuration path:")[1].strip()
                            break
                    
                    success_message = "Profile imported successfully"
                    if config_path:
                        success_message += f"\nConfiguration path: {config_path}"
                    
                    dialog = Gtk.MessageDialog(
                        transient_for=self.window,
                        flags=0,
                        message_type=Gtk.MessageType.INFO,
                        buttons=Gtk.ButtonsType.OK,
                        text=success_message
                    )
                    dialog.run()
                    dialog.destroy()
                    self.load_profiles()
                else:
                    dialog = Gtk.MessageDialog(
                        transient_for=self.window,
                        flags=0,
                        message_type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK,
                        text=f"Error importing profile: {result.stderr}"
                    )
                    dialog.run()
                    dialog.destroy()
            else:
                dialog.destroy()
                
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self.window,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"Error importing profile: {str(e)}"
            )
            dialog.run()
            dialog.destroy()

    def on_connect_clicked(self, button):
        if self.selected_profile_index is not None:
            profile = self.vpn_profiles[self.selected_profile_index]
            
            try:
                # Use the config_path parameter which is the correct way to reference
                # an already imported profile in OpenVPN3
                if "config_path" in profile:
                    # Use config-path for already imported profiles
                    self.status_label.set_text(f"Connecting to {profile.get('display_name', profile.get('name', 'Unknown'))}")
                    result = subprocess.run(
                        ["openvpn3", "session-start", "--config-path", profile["config_path"]],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                elif "file_path" in profile:
                    # Fallback to file_path if we have it
                    self.status_label.set_text(f"Connecting to {profile.get('display_name', profile.get('file_path', 'Unknown'))}")
                    result = subprocess.run(
                        ["openvpn3", "session-start", "--config", profile["file_path"]],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                else:
                    # Last resort, try with the name
                    self.status_label.set_text(f"Connecting to {profile.get('name', 'Unknown')}")
                    result = subprocess.run(
                        ["openvpn3", "session-start", "--config", profile["name"]],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                
                if result.returncode == 0:
                    # Extract session path from output
                    for line in result.stdout.split('\n'):
                        if "Session path: " in line:
                            self.active_connection = line.split("Session path: ")[1].strip()
                            break
                    
                    self.status_label.set_text(f"Connected to {profile.get('display_name', profile.get('name', 'Unknown'))}")
                    self.connect_button.set_sensitive(False)
                    self.disconnect_button.set_sensitive(True)
                    
                    # Start monitoring the session
                    GLib.timeout_add_seconds(2, self.check_connection_status)
                    
                    # Show information about web authentication if needed
                    if "Web based authentication required" in result.stdout:
                        dialog = Gtk.MessageDialog(
                            transient_for=self.window,
                            flags=0,
                            message_type=Gtk.MessageType.INFO,
                            buttons=Gtk.ButtonsType.OK,
                            text="Web authentication required"
                        )
                        dialog.format_secondary_text(
                            "Please complete the authentication in your web browser.\n\n"
                            "The VPN connection will be established once authentication is complete."
                        )
                        dialog.run()
                        dialog.destroy()
                else:
                    self.status_label.set_text("Connection failed")
                    dialog = Gtk.MessageDialog(
                        transient_for=self.window,
                        flags=0,
                        message_type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK,
                        text=f"Connection failed: {result.stderr}"
                    )
                    dialog.run()
                    dialog.destroy()
            except Exception as e:
                self.status_label.set_text("Connection error")
                dialog = Gtk.MessageDialog(
                    transient_for=self.window,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"Error connecting: {str(e)}"
                )
                dialog.run()
                dialog.destroy()

    def on_disconnect_clicked(self, button):
        if self.active_connection:
            try:
                result = subprocess.run(
                    ["openvpn3", "session-manage", "--disconnect", "--path", self.active_connection],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if result.returncode == 0:
                    self.status_label.set_text("Not connected")
                    self.active_connection = None
                    self.connect_button.set_sensitive(True)
                    self.disconnect_button.set_sensitive(False)
                else:
                    dialog = Gtk.MessageDialog(
                        transient_for=self.window,
                        flags=0,
                        message_type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK,
                        text=f"Disconnection failed: {result.stderr}"
                    )
                    dialog.run()
                    dialog.destroy()
            except Exception as e:
                dialog = Gtk.MessageDialog(
                    transient_for=self.window,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"Error disconnecting: {str(e)}"
                )
                dialog.run()
                dialog.destroy()

    def on_delete_profile_clicked(self, button, profile_index):
        """Handle the delete button click for a profile"""
        if profile_index < 0 or profile_index >= len(self.vpn_profiles):
            return
        
        profile = self.vpn_profiles[profile_index]
        profile_name = profile.get("display_name", profile.get("name", "Unknown Profile"))
        
        # Create confirmation dialog
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Remove VPN Profile"
        )
        dialog.format_secondary_text(f"Are you sure you want to remove the profile '{profile_name}'?\n\nThis action cannot be undone.")
        
        response = dialog.run()
        dialog.destroy()
        
        # If user confirms deletion, remove the profile
        if response == Gtk.ResponseType.YES:
            if "config_path" in profile:
                try:
                    # Remove the profile using openvpn3
                    result = subprocess.run(
                        ["openvpn3", "config-remove", "--force", "--path", profile["config_path"]],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        # Show success message
                        self.status_label.set_text(f"Profile '{profile_name}' removed")
                        
                        # Reload profiles
                        self.load_profiles()
                    else:
                        # Show error message
                        error_dialog = Gtk.MessageDialog(
                            transient_for=self.window,
                            flags=0,
                            message_type=Gtk.MessageType.ERROR,
                            buttons=Gtk.ButtonsType.OK,
                            text=f"Error removing profile: {result.stderr}"
                        )
                        error_dialog.run()
                        error_dialog.destroy()
                except Exception as e:
                    # Show error message
                    error_dialog = Gtk.MessageDialog(
                        transient_for=self.window,
                        flags=0,
                        message_type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK,
                        text=f"Error removing profile: {str(e)}"
                    )
                    error_dialog.run()
                    error_dialog.destroy()
    
    def check_connection_status(self):
        if not self.active_connection:
            return False  # Stop the recurring check
            
        try:
            result = subprocess.run(
                ["openvpn3", "session-stats", "--path", self.active_connection],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                # Session probably ended
                self.status_label.set_text("Not connected")
                self.active_connection = None
                self.connect_button.set_sensitive(True)
                self.disconnect_button.set_sensitive(False)
                return False  # Stop the recurring check
            
            return True  # Continue checking
        except Exception:
            self.status_label.set_text("Connection status unknown")
            return True  # Continue checking


if __name__ == "__main__":
    app = OpenVPNClient()
    app.run(None)