
## **Linting**

We use `flake8`, `pylint`, and `mypy` to maintain code quality. Additionally, we've introduced `ruff` to the mix, which covers both linting and formatting. Built in Rust, `ruff` encompasses most of `flake8` and `pylint` functionality (and a bunch of others) but is still under development. The config file includes a lot of up-to-date rules.

```bash
# To check all Python files
flake8 **/*.py
pylint **/*.py
mypy **/*.py
ruff check [optional: file]  # to list linting warnings and errors
ruff check --fix [optional: file]  # to fix them automatically
```

## **Formatting**

`ruff` handles formatting in a similar way that `black` does; it can be very opinionated but also customizable.

```bash
ruff format --help  # to see all available options
ruff format --diff [file]  # will print the proposed changes
ruff format [file]  # regular formatting operation
```

## **Testing and Coverage**

`pytest` is used for running tests, and `coverage` generates a coverage report using `pytest`.

```bash
pytest  # will run the whole suite of tests
coverage run -m pytest  # to generate a coverage report
coverage report -m  # to see the report
```

## **pre-commit checks**

`pre-commit` is a tool that installs hooks on git's functionality. When that functionality is called to run, the hooks are ran first. This enables testing, linting, and formatting to automatically run consistently every time that git functionality is called.

To install (or uninstall) the hooks, activate the environment and run:

```sh
$ pre-commit install  # uninstall
pre-commit installed at .git/hooks/pre-commit
pre-commit installed at .git/hooks/pre-push
```

To temporarily skip over a hook; if you're fixing the issue in a later commit, for example a failed test, use:

```sh
SKIP pytest-check git commit -m "Commit message.."
```

## UV Package Manager (optional)

`uv` is a modern Python package manager, written in Rust. It replaces `venv`, `virtualenv`, `poetry`, `anaconda` (for projects that don't need binaries), and other tools.

### Installation

It is available to install as a standalone script (always review such scripts before running!) or through other sources. More information in the [documentation](https://github.com/astral-sh/uv?tab=readme-ov-file#getting-started).

To update: `uv self update`

### Usage

`uv` is a drop-in replacement for `pip`. However, choose one or the other for each virtual environment as they are not interchangeable.

```bash
# Create a virtual environment
uv venv .venv  # defaults to .venv but can be changed
source .venv/bin/activate

uv pip install .  # Install runtime dependencies
uv pip install .[dev]  # Install development dependencies
```
