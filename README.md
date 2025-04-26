# Projects Tools

A command line tool for managing projects with LLM integration.

## Features

- **Project Creation**: Create Python backend and frontend (React/Vue) projects
- **LLM Integration**: Generate code, analyze codebases, and debug components using LLMs
- **Project Analysis**: Analyze codebases and generate insights
- **Configuration Management**: Centralized configuration system
- **Error Handling**: Comprehensive error handling and validation

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- For frontend development: Node.js and npm

### Install from PyPI

```bash
pip install projects-tools
```

### Install from Source

1. Clone the repository
```bash
git clone https://github.com/Zeeeepa/project_tools.git
cd project_tools
```

2. Install in development mode
```bash
pip install -e .
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

To use the LLM integration features, you need to set up API keys for the LLM providers:

### OpenAI

```bash
# Linux/macOS
export OPENAI_API_KEY=your_key_here

# Windows (Command Prompt)
set OPENAI_API_KEY=your_key_here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your_key_here"
```

### Anthropic

```bash
# Linux/macOS
export ANTHROPIC_API_KEY=your_key_here

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your_key_here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your_key_here"
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
```

6. Sort imports
```bash
isort src tests
```

7. Type check
```bash
mypy src
```

## Deployment

### Linux/macOS

```bash
# Deploy in development mode
./deploy.sh dev

# Deploy in release mode (will upload to PyPI)
./deploy.sh
```

### Windows

```batch
# Deploy in development mode
deploy.bat dev

# Deploy in release mode (will upload to PyPI)
deploy.bat
```

## Project Structure

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
│   │   ├── code_generator.py
│   │   ├── codebase_analyzer.py
│   │   ├── context_manager.py
│   │   ├── db_schema_generator.py
│   │   ├── error_collector.py
│   │   ├── feedback_loop.py
│   │   ├── llm_client.py
│   │   ├── project_genie.py
│   │   ├── runtime_validator.py
│   │   ├── test_generator.py
│   │   └── validator.py
│   ├── templates/            # Templates
│   │   └── ...
│   ├── templating/           # Templating system
│   │   ├── __init__.py
│   │   ├── algorithms.py
│   │   ├── component_generator.py
│   │   ├── layout_generator.py
│   │   ├── pattern_generator.py
│   │   ├── template_context.py
│   │   ├── template_manager.py
│   │   └── template_registry.py
│   └── utils/                # Shared utilities
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       ├── logging.py        # Logging utilities
│       └── errors.py         # Error handling
```

## Configuration

The tool can be configured using:

1. Configuration files:
   - `.projects_tools.json` in the current directory
   - `.projects_tools.json` in the user's home directory
   - `.config/projects_tools.json` in the user's home directory

2. Environment variables:
   - Prefixed with `PROJECTS_TOOLS_`
   - For nested configuration, use double underscore as separator
   - Example: `PROJECTS_TOOLS_LLM__DEFAULT_PROVIDER=openai`

3. CLI arguments:
   - Using the `configure` command
   - Example: `projects configure --set llm.default_provider anthropic`

## Troubleshooting

### Common Issues

1. **Missing API Keys**:
   - Ensure you've set the appropriate environment variables for your LLM provider.

2. **Package Not Found**:
   - Make sure the package is installed correctly: `pip list | grep projects-tools`

3. **Permission Issues**:
   - On Linux/macOS, make sure the deploy script is executable: `chmod +x deploy.sh`

4. **Frontend Creation Fails**:
   - Ensure Node.js and npm are installed and in your PATH.

## License

MIT
