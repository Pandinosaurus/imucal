import shutil
from pathlib import Path
import platform

DOIT_CONFIG = {
    "default_tasks": ["format", "test", "lint"],
    "backend": "json",
}

HERE = Path(__file__).parent


def task_format():
    """Reformat all files using black."""
    return {"actions": [["black", HERE]], "verbosity": 1}


def task_format_check():
    """Check, but not change, formatting using black."""
    return {"actions": [["black", HERE, "--check"]], "verbosity": 1}


def task_test():
    """Run Pytest with coverage."""
    return {"actions": [["pytest", "--cov=imucal"]], "verbosity": 2}


def task_lint():
    """Lint all files with Prospector."""
    return {"actions": [["prospector"]], "verbosity": 1}


def task_docs():
    """Build the html docs using Sphinx."""
    # Copy the README into the docs folder
    # shutil.copy(str(HERE / "README.md"), str(HERE / "docs"))
    # # Delete Autogenerated files from previous run
    # shutil.rmtree(str(HERE / "docs/modules/generated"), ignore_errors=True)

    if platform.system() == "Windows":
        return {"actions": [[HERE / "docs/make.bat", "html"]], "verbosity": 2}
    else:
        return {"actions": [["make", "-C", HERE / "docs", "html"]], "verbosity": 2}
