from setuptools import setup, find_packages

setup(
    name="gutshape",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["pyyaml", "loguru", "typer", "rich", "pathspec"],
    entry_points={"console_scripts": ["gutshape=gutshape.cli:app"]},
)
