# Python Practice Repository

This is a practice repository where I develop Python projects and experiments on various topics. The goal is to improve my Python skills and explore different areas of programming.

## Project Structure

- `bamboohr_api_people_tests/`: Tests and experiments with BambooHR API
- `notebooks/`: Jupyter notebooks for data analysis and experiments
- `spark-lab/`: Apache Spark related experiments and tests
- `slack_channel_configs/`: Slack integration configurations
- `tests-scripts/`: Various test scripts and utilities
- `yaml_template_test/`: YAML template testing and experiments

## Development Tools

This project uses several development tools and libraries:

- **uv** for dependency management and virtual environment handling
- **Black** and **isort** for code formatting
- **Flake8**, **Pylint**, and **MyPy** for code quality and type checking
- **Pytest** for testing with coverage reporting
- **Jupyter** for interactive development
- **Pre-commit** for git hooks

## Setup Instructions

Before you start coding, you need to set up a virtual environment and install the necessary dependencies using uv.

1. **Install uv** (if not already installed):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. **Create and activate a virtual environment with uv:**
    ```bash
    uv venv
    source .venv/bin/activate  # On macOS/Linux
    # or
    .\.venv\Scripts\activate  # On Windows
    ```

3. **Install dependencies with uv:**
    ```bash
    uv pip install -e .
    ```

4. **Set up pre-commit hooks:**
    ```bash
    pre-commit install
    ```

## Development Workflow

1. Create a new branch for your feature or fix
2. Make your changes
3. Run the following checks before committing:
   ```bash
   black .
   isort .
   flake8
   mypy .
   pytest
   ```
4. Commit your changes with a descriptive message
5. Create a pull request

## License

This project is licensed under the terms of the LICENSE file in the root of this repository.