# Python Practice Repository

This is a practice repository where I develop Python projects and experiments on various topics. The goal is to improve my Python skills and explore different areas of programming.

## Project Structure

- `api_lab/`: API development and testing experiments
  - Contains API implementations and data handling
- `spark-lab/`: Apache Spark related experiments and tests
  - `delta-lab/`: Delta Lake experiments
  - `learning-spark/`: Spark learning materials and examples
  - `mnm_playground/`: MNM dataset experiments
  - `datasets/`: Sample datasets for Spark experiments
- `slack_channel_configs/`: Slack integration configurations
- `scripts/`: Utility scripts and tools

## Development Tools

This project uses several development tools and libraries:

- **uv** for dependency management and virtual environment handling
- **Ruff** for fast Python linting and formatting
- **MyPy** for static type checking
- **Pre-commit** for git hooks
- **Jupyter** for interactive development

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
   ruff check .
   ruff format .
   mypy .
   ```
4. Commit your changes with a descriptive message
5. Create a pull request

## License

This project is licensed under the terms of the LICENSE file in the root of this repository.
