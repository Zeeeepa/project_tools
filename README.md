# Projects Tools

A command line tool for managing projects with LLM integration.

## Features

- **Project Creation**: Create Python backend and frontend (React/Vue) projects
- **LLM Integration**: Generate code, analyze codebases, and debug components using LLMs
- **Project Analysis**: Analyze codebases and generate insights
- **Configuration Management**: Centralized configuration system
- **Error Handling**: Comprehensive error handling and validation
- **Template System**: Flexible templating for project generation

## Installation

```bash
pip install projects-tools
```

## Usage

### Create a new project

```bash
# Create a Python backend project
projects create my-project --backend

# Create a frontend project with React
projects create my-project --frontend --frontend_type reactjs

# Create a full-stack project with Vue frontend and proxy server
projects create my-project --backend --frontend --frontend_type vue --enable_proxy

# Create a project with LLM-assisted code generation
projects create my-project --backend --frontend --llm-assisted
```

### Generate code from description

```bash
projects genie "Create a REST API for a blog with user authentication"
```

### Debug a component

```bash
projects debug src/my_component.py "The authentication is not working correctly"
```

### Analyze a codebase

```bash
projects analyze_codebase --output-file analysis.json
```

### Configure the tool

```bash
# Show current configuration
projects configure --show

# Set configuration values
projects configure --set llm.default_provider anthropic

# Save configuration
projects configure --save
```

## LLM Integration

This tool integrates with OpenAI and Anthropic APIs to provide AI-assisted features:

### Setting up API Keys (Development)

For development environments only:
```bash
export OPENAI_API_KEY=your_key_here
export ANTHROPIC_API_KEY=your_key_here
```

For production, we recommend using a secrets manager or encrypted configuration files. See our [Security Best Practices](docs/security.md) guide.

### Available LLM Features

- **Code Generation**: Generate code based on natural language descriptions
- **Codebase Analysis**: Analyze codebases and generate insights
- **Component Debugging**: Debug components based on issue descriptions
- **Test Generation**: Generate tests for components
- **Database Schema Generation**: Generate database schemas from descriptions

## Project Structure

The project is organized into the following modules:

```
src/
├── projects_tools/
│   ├── __init__.py
│   ├── version.py
│   ├── cli/                  # CLI-specific code
│   │   ├── __init__.py
│   │   ├── commands.py       # Command definitions
│   │   ├── formatters.py     # Output formatting
│   │   └── validators.py     # CLI input validation
│   ├── llm_integration/      # LLM integration
│   │   ├── __init__.py
│   │   ├── llm_client.py     # LLM client
│   │   ├── code_generator.py # Code generation
│   │   ├── codebase_analyzer.py # Codebase analysis
│   │   └── ...
│   ├── templating/           # Templating system
│   │   ├── __init__.py
│   │   ├── template_manager.py
│   │   ├── component_generator.py
│   │   └── ...
│   ├── templates/            # Template files
│   │   ├── components/
│   │   ├── layouts/
│   │   └── ...
│   └── utils/                # Shared utilities
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       ├── logging.py        # Logging utilities
│       └── errors.py         # Error handling
```

## Development

To set up the development environment:

1. Clone the repository
   ```bash
   git clone https://github.com/Zeeeepa/project_tools.git
   cd project_tools
   ```

2. Install in development mode
   ```bash
   pip install -e .
   ```

3. Install development dependencies
   ```bash
   pip install pytest black isort mypy
   ```

4. Run tests
   ```bash
   pytest
   ```

5. Format code
   ```bash
   black src tests
   isort src tests
   ```

6. Type check
   ```bash
   mypy src
   ```

## Deployment

### Linux/macOS

Use the provided deployment script:

```bash
./deploy.sh
```

### Windows

Use the provided batch file:

```cmd
deploy.bat
```

## Configuration

The tool uses a hierarchical configuration system with the following precedence:

1. Command-line arguments
2. Environment variables
3. Configuration file
4. Default values

### Configuration File

The default configuration file is located at `~/.config/projects_tools/config.json`.

Example configuration:

```json
{
  "llm": {
    "default_provider": "openai",
    "openai": {
      "model": "gpt-4",
      "timeout": 30,
      "retry_attempts": 3
    },
    "anthropic": {
      "model": "claude-3-opus-20240229"
    }
  },
  "project": {
    "default_frontend": "reactjs"
  },
  "templates": {
    "path": "./custom_templates",
    "default_component": "basic"
  },
  "logging": {
    "level": "INFO",
    "file": "~/.logs/projects_tools.log"
  },
  "error_handling": {
    "retry_enabled": true,
    "max_retries": 3
  }
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
