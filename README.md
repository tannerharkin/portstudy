# PortStudy

A command-line utility for learning and practicing network port numbers and protocols. Perfect for IT certification exam preparation or general networking knowledge enhancement.

![MPL-2.0 License](https://img.shields.io/badge/License-MPL_2.0-blue.svg)![Python Versions](https://img.shields.io/badge/python-3.8%2B-blue)![Development Status](https://img.shields.io/badge/status-beta-yellow)

## Features

- Progressive difficulty levels that adapt to your learning pace
- Smart question generation based on performance
- Multiple question types including:
  - Port number to protocol matching
  - Protocol to port number identification
  - Transport protocol identification
  - Usage and description comprehension
- Persistent progress tracking with secure save states
- Cross-platform support (Windows, macOS, Linux)
- Designed with educational environments in mind:
  - User save data is stored under the Roaming AppData profile on Windows
  - Windows binaries that are made available come pre-signed for AppLocker environments


## Installation

### Recommended: Using pip

You can install PortStudy using pip:

```bash
pip install portstudy
```

For the latest development version:

```bash
pip install git+https://github.com/tannerharkin/portstudy.git@main
```

### Alternative: Standalone Binaries

For environments where installing Python and pip isn't feasible (such as restricted educational environments), you can download pre-built standalone binaries from the [Releases](https://github.com/tannerharkin/portstudy/releases) page.

These binaries:
- Require no Python installation (or even network access) on the host machine
- Are self-signed for compatibility with AppLocker environments
- Run on Windows without additional dependencies
- Are portable (can be run from USB drives)

**Note**: While standalone binaries are convenient, the pip installation method is recommended when possible as it provides automatic updates and better integration with the Python ecosystem. Additionally, the standalone binary isn't the fastest thing to start since it is using a bundled Python interpreter. That being said, we know many environments see the static nature of these binaries as an advantage, and that is why they have been made readily available and are considered supported.

## Usage

After installation, you can start PortStudy by running:

```bash
portstudy
```

Or using Python's module syntax:

```bash
python -m portstudy
```

### Study Modes

1. **Practice Mode**: Test your knowledge with dynamically generated questions
2. **View Statistics**: Track your progress and performance
3. **Exit**: Save and quit the application

### Difficulty Levels

The application features 5 progressive difficulty levels:

- Level 1: Basic port/protocol pairs
- Level 2: Adds transport protocol questions
- Level 3: Introduces 'intermediate' ports and usage questions
- Level 4: Adds direct port entry questions
- Level 5: Includes 'advanced' ports

Progress through levels is based on maintaining consistent accuracy and answer streaks.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the Mozilla Public License Version 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Special thanks to [Colorama](https://github.com/tartley/colorama) for making terminals across platforms a little bit easier to deal with.

## Project Status

PortStudy is currently beta software. While it is stable for daily use, some features are still under development and interfaces may change. If you rely on this tool for a course, I highly recommend making your own fork so you can control changes.

## Support

If you encounter any issues or have questions:

1. Check the [issues page](https://github.com/tannerharkin/portstudy/issues)
2. Submit a new issue with a detailed description
3. Contact the maintainers

Please note that this is an open-source utility run by a college student. Support may not be all that fast, however, most issues are easily resolved since I have attempted to leave a significant amount of documentation to aid you.
