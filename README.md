# External IP Service

A CLI service for displaying external IP information, **designed specifically for Polybar integration**. The service runs in the background, periodically fetches IP information from [ipinfo.io](https://ipinfo.io), and serves it via a Unix socket for fast client access. The client command is optimized for use with Polybar's `custom/script` module.

## Features

- 🔄 **Background Service**: Runs as a daemon, continuously fetching and caching IP information
- 🌐 **IP Information**: Retrieves IP address, ASN, AS name, country, and continent data
- 🔌 **Unix Socket Communication**: Fast, local IPC via Unix domain sockets
- 📊 **Network Change Detection**: Monitors iptables changes to detect network configuration updates
- 🎨 **Customizable Output**: Template-based formatting for client output
- 📝 **Configurable Logging**: Flexible logging with support for different levels, formats, and outputs

## Architecture

The project consists of two main components:

1. **Service** (`extip service`): A background daemon that:
   - Fetches IP information from ipinfo.io API
   - Serves data via Unix socket (`/tmp/extip.sock` by default)
   - Monitors iptables for network changes
   - Periodically updates IP information

2. **Client** (`extip client`): A lightweight client **designed for Polybar** that:
   - Connects to the service socket
   - Retrieves current IP information
   - Formats and displays the data using templates
   - Outputs to stdout for seamless Polybar integration
   - Handles service states (ready, updating, error) gracefully

## Installation

### Requirements

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- [moon](https://moonrepo.dev/) (for development)

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd external-ip-service

# Install dependencies and build
cd apps/cli
uv sync
uv pip install -e .
```

## Usage

### Starting the Service

```bash
# Start the service with default settings
extip service

# With IPinfo.io token (recommended for higher rate limits)
extip service --token YOUR_TOKEN
# or set environment variable
export EXTIP_TOKEN=YOUR_TOKEN
extip service

# Custom socket path
extip service --socket-path /path/to/socket.sock

# Custom log level
extip service --log-level DEBUG

# Log to file
extip service --log-file /path/to/logfile.log

# Enable colorized output
extip service --log-colorize
```

### Using the Client (Polybar Integration)

The `extip client` command is **designed to be used with Polybar's `custom/script` module**. It outputs formatted text to stdout, making it perfect for status bar integration.

```bash
# Default format (ASN and IP)
extip client

# Custom format for Polybar
extip client --info-format "{{info.ip}} ({{info.country_code}})"

# Available template variables:
# - {{info.ip}} - IP address
# - {{info.asn}} - ASN number
# - {{info.as_name}} - AS name
# - {{info.as_domain}} - AS domain
# - {{info.country_code}} - Country code (e.g., "US")
# - {{info.country}} - Country name
# - {{info.continent_code}} - Continent code (e.g., "NA")
# - {{info.continent}} - Continent name
# - {{status}} - Service status (ready, updating, error)
```

**Note**: The client automatically handles service states:
- When service is ready: outputs formatted IP information
- When service is updating: outputs "Updating..."
- When service has an error: outputs "Service error"
- When service is not running: outputs "Service is not started"

### Environment Variables

- `EXTIP_TOKEN`: IPinfo.io API token (optional but recommended)
- `EXTIP_SOCKET`: Path to Unix socket (default: `/tmp/extip.sock`)
- `EXTIP_LOG_LEVEL`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `EXTIP_LOG_COLORIZE`: Enable colorized output (true/false)
- `EXTIP_LOG_FORMAT`: Custom log format string
- `EXTIP_LOG_FILE`: Path to log file (if not set, logs to stdout/stderr)

## Development

This project uses [moon](https://moonrepo.dev/) for task management and [uv](https://github.com/astral-sh/uv) for package management.

### Setup

```bash
# Install moon (if not already installed)
# See: https://moonrepo.dev/docs/install

# Install uv (if not already installed)
# See: https://github.com/astral-sh/uv

# Sync dependencies
cd apps/cli
uv sync
```

### Running Tests

```bash
cd apps/cli
uv run pytest
```

### Linting and Formatting

```bash
# Lint
moon run extip:lint

# Format
moon run extip:format

# Both (via pre-commit hook)
moon run :lint :format --affected --status=staged
```

### Building

```bash
cd apps/cli
uv build
```

### Publishing

```bash
# Update version
moon extip:version -- [version_update]

# Publish
moon extip:publish --dependents
```

## Project Structure

```
external-ip-service/
├── apps/
│   └── cli/              # Main CLI application
│       ├── src/extip/
│       │   ├── cli.py           # CLI entry point
│       │   ├── commands/        # CLI commands
│       │   │   ├── client.py    # Client command
│       │   │   └── service.py   # Service command
│       │   ├── service.py       # Service implementation
│       │   └── utils/           # Utilities
│       │       ├── __init__.py  # IP info client
│       │       └── iptables.py  # iptables monitoring
│       └── tests/               # Test suite
├── docs/                 # Documentation
└── uv.toml              # UV configuration
```

## Logging

The service supports flexible logging configuration:

- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Output Separation**: INFO/WARNING/DEBUG → stdout, ERROR/CRITICAL → stderr
- **Custom Formats**: Configurable log format using loguru syntax
- **File Logging**: Optional file output
- **Colorization**: Optional colored output for terminals

Example log format:
```
<green>2024-01-01 12:00:00.000</green> | <level>INFO    </level> | <cyan>extip</cyan>:<cyan>service</cyan>:<cyan>88</cyan> - <level>Starting service...</level>
```

## Polybar Integration

The client is **specifically designed for Polybar** and works seamlessly with Polybar's `custom/script` module. Here are example configurations:

### Basic Setup

First, ensure the service is running (see [Starting the Service](#starting-the-service) above), then add this to your Polybar config:

```ini
[module/extip]
type = custom/script
exec = extip client --info-format "{{info.ip}}"
interval = 5
format = <label>
label = %output%
```

Or for more detailed information:

```ini
[module/extip]
type = custom/script
exec = extip client --info-format "{{info.ip}} ({{info.country_code}})"
interval = 5
format = <label>
label = %output%
```

### Advanced Configuration

You can customize the output format and update interval based on your needs:

```ini
[module/extip]
type = custom/script
exec = extip client --info-format "🌐 {{info.ip}}"
interval = 10
format = <label>
label = %output%
format-padding = 2
```

### With Click Actions

```ini
[module/extip]
type = custom/script
exec = extip client --info-format "{{info.ip}}"
interval = 5
format = <label>
label = %output%
click-left = extip client --info-format "IP: {{info.ip}} | ASN: {{info.asn}} | Country: {{info.country}}"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing
