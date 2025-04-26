# Project Tools

A command line tool for managing projects with LLM integration. This tool helps developers create, analyze, and debug projects using AI assistance.

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
- For LLM features: OpenAI or Anthropic API key

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

2. Install the package
```bash
pip install -e .
```

## Configuration

### API Keys

To use LLM-assisted features, you need to set up API keys:

**For OpenAI:**
```bash
# Linux/macOS
export OPENAI_API_KEY=your_key_here

# Windows (Command Prompt)
set OPENAI_API_KEY=your_key_here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your_key_here"
```

**For Anthropic:**
```bash
# Linux/macOS
export ANTHROPIC_API_KEY=your_key_here

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your_key_here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="your_key_here"
```

### Tool Configuration

You can configure the tool using the `configure` command:

```bash
# Show current configuration
projects configure --show

# Set configuration values
projects configure --set llm.default_provider anthropic
projects configure --set project.default_frontend vue

# Save configuration
projects configure --save
```

## Usage

### Create a New Project

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

### Generate Code from Description

The `genie` command uses LLMs to generate code based on natural language descriptions:

```bash
projects genie "Create a REST API for a blog with user authentication" --project-path ./my-project
```

### Debug a Component

The `debug` command helps identify and fix issues in your code:

```bash
projects debug src/my_component.py "The authentication is not working correctly" --project-path ./my-project
```

### Analyze a Codebase

The `analyze_codebase` command provides insights about your project:

```bash
# Basic analysis
projects analyze_codebase --project-path ./my-project

# Analysis with specific include/exclude patterns
projects analyze_codebase --include-patterns "*.py" --exclude-patterns "tests/*" --project-path ./my-project

# Save analysis to a file
projects analyze_codebase --output-file analysis.json --project-path ./my-project
```

## Deployment

### Linux/macOS

```bash
# Clone the repository
git clone https://github.com/Zeeeepa/project_tools.git
cd project_tools

# Run the deployment script
chmod +x deploy.sh
./deploy.sh
```

### Windows

```batch
# Clone the repository
git clone https://github.com/Zeeeepa/project_tools.git
cd project_tools

# Run the deployment script
deploy.bat
```

## Project Structure

```
src/
├── projects_tools/
│   ├── __init__.py
│   ├── version.py
│   ├── commands.py
│   ├── react_tasks.py
│   ├── vue_tasks.py
│   ├── cli/                  # CLI-specific code
│   │   ├── __init__.py
│   │   ├── commands.py       # Command definitions
│   │   ├── formatters.py     # Output formatting
│   │   └── validators.py     # CLI input validation
│   ├── llm_integration/      # LLM integration
│   │   ├── __init__.py
│   │   ├── llm_client.py     # LLM API clients
│   │   ├── code_generator.py # Code generation
│   │   ├── codebase_analyzer.py # Codebase analysis
│   │   ├── context_manager.py # Context management
│   │   ├── project_genie.py  # Natural language to code
│   │   └── ...
│   ├── templates/            # Templates for code generation
│   │   ├── components/       # Component templates
│   │   ├── layouts/          # Layout templates
│   │   └── patterns/         # Pattern templates
│   ├── templating/           # Template processing
│   │   ├── __init__.py
│   │   ├── template_manager.py
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

2. Create a virtual environment (optional but recommended)
```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. Install in development mode
```bash
pip install -e .
```

4. Install development dependencies
```bash
pip install pytest black isort mypy
```

5. Run tests
```bash
pytest
```

6. Format code
```bash
black src tests
isort src tests
```

7. Type check
```bash
mypy src
```

## Troubleshooting

### API Key Issues

If you encounter errors related to API keys:

1. Verify that your API key is set correctly in the environment
2. Check that you have sufficient credits/quota with your API provider
3. Ensure you're using a supported model

### Installation Issues

If you encounter installation problems:

1. Ensure you have Python 3.9 or higher installed
2. Update pip: `pip install --upgrade pip`
3. Try installing with verbose output: `pip install -v projects-tools`

### Command Errors

If commands fail:

1. Check the error message for specific issues
2. Verify that your project structure is correct
3. Ensure you have the necessary permissions for file operations

## License

MIT
