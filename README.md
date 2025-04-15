# Projects Tools

A command line tool for managing projects with LLM integration.

## Features

- **Project Creation**: Create Python backend and frontend (React/Vue) projects
- **LLM Integration**: Generate code, analyze codebases, and debug components using LLMs
- **Project Analysis**: Analyze codebases and generate insights
- **Configuration Management**: Centralized configuration system
- **Error Handling**: Comprehensive error handling and validation

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

## Development

To set up the development environment:

1. Clone the repository
2. Run `pip install -e .`
3. Install development dependencies: `pip install pytest black isort mypy`
4. Run tests: `pytest`
5. Format code: `black src tests`
6. Sort imports: `isort src tests`
7. Type check: `mypy src`

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
│   ├── core/                 # Core business logic
│   │   ├── __init__.py
│   │   ├── project.py        # Project management
│   │   ├── generator.py      # Code generation
│   │   └── analyzer.py       # Code analysis
│   ├── frontend/             # Frontend generation
│   │   ├── __init__.py
│   │   ├── react.py
│   │   └── vue.py
│   ├── llm/                  # LLM integration
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── context.py
│   │   ├── generator.py
│   │   └── analyzer.py
│   ├── templates/            # Templates
│   │   └── ...
│   └── utils/                # Shared utilities
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       ├── logging.py        # Logging utilities
│       └── errors.py         # Error handling
```

## License

MIT
