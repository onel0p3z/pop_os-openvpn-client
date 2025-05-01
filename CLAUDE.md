# CLAUDE.md - Guidelines for Pop!_OS OpenVPN Client

## Commands
- Run application: `python3 src/openvpn_client.py`
- Run all tests: `python3 -m unittest discover src`
- Run single test file: `python3 -m unittest src/test_improvements.py`
- Run specific test: `python3 -m unittest src.test_improvements.TestRefreshButton.test_refresh_button_exists`
- Check syntax: `python3 -m py_compile src/openvpn_client.py`

## Code Style
- **Imports**: Group imports by standard library, third-party (gi/Gtk), then local
- **Spacing**: 4 spaces for indentation, no tabs
- **Naming**: snake_case for variables/functions, CamelCase for classes, UPPER_CASE for constants
- **Documentation**: Docstrings for classes and methods using triple double-quotes (""")
- **Error handling**: Use try/except blocks with specific exception types where possible
- **GTK widgets**: Create widgets before connecting signals, use consistent naming for callbacks (on_*_clicked)
- **Subprocess**: Always capture stdout/stderr when running commands, check return code

## Testing
- Create separate test files for distinct features
- Use unittest.TestCase and descriptive test method names
- Write code-inspection tests for GTK features to avoid UI testing complexity 
- Handle GTK specifics (like dialogs) through mocking
- Include verification messages in assertions