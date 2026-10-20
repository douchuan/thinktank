# uv Command Cheat Sheet

Applicable to: macOS / Linux, Python 3.12, AI Agent & CrewAI projects

Official docs: [uv Documentation](https://docs.astral.sh/uv/) · [Complete CLI Reference](https://docs.astral.sh/uv/reference/cli/).

This cheat sheet is organized by everyday development workflow, covering the most commonly used commands first. uv's project mode automatically handles lock files and environment synchronization, so in most cases you don't need to manually activate a virtual environment.


## 1. Installation & Version Management

| Command                        | Purpose                          |
| ------------------------------ | -------------------------------- |
| `brew install uv`              | Install uv via Homebrew on macOS |
| `uv --version`                 | Check uv version                 |
| `uv self update`               | Update uv itself                 |
| `uv python list`               | List available Python versions   |
| `uv python install 3.12`       | Install Python 3.12              |
| `uv python find 3.12`          | Find the path to Python 3.12     |
| `uv python pin 3.12`           | Pin Python version for the current project |
| `uv python uninstall 3.12`     | Uninstall uv-managed Python 3.12 |

Note: `uv python uninstall` removes interpreters managed by uv; it should not be used to uninstall system or Homebrew-managed Python.

## 2. Creating a Project

| Command                            | Purpose                               |
| ---------------------------------- | ------------------------------------- |
| `uv init my-project`               | Create a new Python project           |
| `uv init --package my-project`     | Create a package project suitable for building and installing |
| `uv init --bare my-project`        | Create a minimal project skeleton       |
| `uv init`                          | Initialize a project in the current directory |
| `uv sync`                          | Create environment and sync dependencies |
| `uv sync --extra dev`              | Sync project and optional `dev` dependency group |

## 3. Virtual Environment Management

| Command                         | Purpose                                      |
| ------------------------------- | -------------------------------------------- |
| `uv venv`                       | Create `.venv` virtual environment           |
| `uv venv --python 3.12`         | Create environment using Python 3.12         |
| `uv venv .venv-dev`             | Create an environment with a custom name     |
| `source .venv/bin/activate`     | Activate the virtual environment             |
| `deactivate`                    | Exit the virtual environment                 |
| `uv run python --version`       | Check the actual Python version in use       |
| `uv run which python`           | Show the Python path at runtime (macOS/Linux)|

Recommended project mode: Run `uv sync` first and let uv automatically create and maintain `.venv`. Use `uv venv` directly only when you need manual environment control.

## 4. Dependency Management

This is the most important set of commands for daily development.

| Command                 | Purpose                                |
| ----------------------- | -------------------------------------- |
| `uv add requests`       | Add a runtime dependency               |
| `uv add crewai`         | Add CrewAI                             |
| `uv add --dev pytest`   | Add a development dependency           |
| `uv remove requests`    | Remove a dependency                    |
| `uv sync`               | Sync project dependencies              |
| `uv sync --locked`      | Require lock file is up-to-date, or fail |
| `uv lock`               | Generate or update the lock file       |
| `uv lock --upgrade`     | Update dependency resolution, attempting to upgrade to the latest allowed version |
| `uv tree`               | View the dependency tree               |
| `uv tree --outdated`    | Show dependencies with available updates |
| `uv pip list`           | List packages installed in the current environment |
| `uv pip show crewai`    | Show details for a specific package    |

For example, to add FastAPI and a dev dependency:

```
uv add fastapi
uv add --dev httpx
uv sync
```

`uv add` updates `pyproject.toml`, the lock file, and the environment; you usually don't need to run `uv sync` separately afterwards.


## 5. Running Programs & Scripts

| Command                                  | Purpose                        |
| ---------------------------------------- | ------------------------------ |
| `uv run python main.py`                  | Run a Python program           |
| `uv run pytest`                          | Run tests                      |
| `uv run ruff check .`                    | Lint code                      |
| `uv run ruff format .`                   | Format code                    |
| `uv run mypy src/`                       | Run type checking              |
| `uv run -- python -c "print('hello')"`   | Execute a Python one-liner     |
| `uv run --no-sync python main.py`        | Run without syncing the environment first |
| `uv run --locked pytest`                 | Refuse to run if lock file is stale |

For the Hundred Schools project, common commands include:

```
# Run the advisory
uv run hundred-schools "How to manage a team?"

# Run tests
uv run pytest

# Lint code
uv run ruff check .

# Check formatting
uv run ruff format --check .
```

`uv run` doesn't just call Python — it also checks whether the project environment needs syncing. `--no-sync` skips the check, but only use it when the environment is already ready.


## 6. Lock Files & Team Collaboration

`uv.lock` records resolved dependency versions, helping different developers and CI environments reproduce consistent dependency sets.

| Command                               | Purpose                              |
| ------------------------------------- | ------------------------------------ |
| `uv lock`                             | Update the lock file                 |
| `uv lock --check`                     | Check whether the lock file is up-to-date |
| `uv sync --locked`                    | Fail directly if the lock file doesn't match |
| `uv sync --frozen`                    | Use the existing lock file without updating it |
| `uv export --format requirements.txt` | Export as requirements.txt           |
| `uv tree`                             | View dependency relationships        |

Recommended team development practices:

- Commit both `pyproject.toml` and `uv.lock` to Git.
- Do not commit `.venv/`.
- After changing dependencies, verify the lock file is updated.
- Use `uv sync --locked` in CI to avoid accidentally modifying the lock file during builds.

Note: `--locked` and `--frozen` are not the same — the former checks whether the lock file is stale, while the latter trusts the existing lock file directly.

## 7. Tool Installation & Temporary Execution

uv can also replace some `pipx` workflows for installing or temporarily running standalone Python CLI tools.

| Command                    | Purpose                               |
| -------------------------- | ------------------------------------- |
| `uvx ruff check .`         | Run Ruff in a temporary tool environment |
| `uv tool install ruff`     | Install Ruff as a global CLI tool     |
| `uv tool list`             | List installed tools                  |
| `uv tool upgrade ruff`     | Upgrade a specific tool               |
| `uv tool upgrade --all`    | Upgrade all installed tools           |
| `uv tool uninstall ruff`   | Uninstall a specific tool             |

Key differences:

- `uv add --dev ruff`: Adds Ruff as a dev dependency for the current project, enabling team reproducibility.
- `uv tool install ruff`: Installs Ruff as a standalone global tool.
- `uvx ruff`: Runs a tool temporarily without adding it to the current project's dependencies.

Use the first option for project development; use the latter two for one-off checks or personal global tools.

## 8. Legacy pip Workflow Compatibility

If you're maintaining an older project that hasn't adopted the `pyproject.toml` project mode, you can use uv's pip-compatible interface.

| Command                                                | Purpose                              |
| ------------------------------------------------------ | ------------------------------------ |
| `uv pip install requests`                              | Install a Python package             |
| `uv pip install -r requirements.txt`                   | Install from a requirements file     |
| `uv pip uninstall requests`                            | Uninstall a package                  |
| `uv pip list`                                          | List installed packages              |
| `uv pip freeze`                                        | Export current environment's package versions |
| `uv pip compile requirements.in -o requirements.txt`   | Resolve and generate a locked dependency list |
| `uv pip sync requirements.txt`                         | Sync environment to the specified package set |

These commands suit traditional `requirements.txt` workflows. For new projects, prefer `uv add`, `uv sync`, and `uv.lock` — don't maintain two dependency management systems simultaneously.


## 9. One-Page Quick Reference: The 12 Most Worth Memorizing

```bash

# Check if uv is installed
uv --version

# Install Python 3.12
uv python install 3.12

# Pin the project's Python version
uv python pin 3.12

# Create a new project
uv init my-project

# Install and sync project dependencies
uv sync

# Add a project dependency
uv add requests

# Add a dev dependency
uv add --dev pytest

# Remove a project dependency
uv remove requests

# Run a program
uv run python main.py

# Run tests
uv run pytest

# View the dependency tree
uv tree

# Strictly sync using the latest lock file
uv sync --locked

```

Remember this core workflow:

New project

`uv init` → `uv add` → `uv run`

Existing project

`uv sync` → `uv run` → `uv lock`

Team collaboration

Commit `pyproject.toml` and `uv.lock`, verify with `uv sync --locked`.

Full commands are always available in the [uv official CLI reference](https://docs.astral.sh/uv/reference/cli/).
