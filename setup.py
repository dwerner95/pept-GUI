"""Python setup.py for pept_gui package"""
import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("pept_gui", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="pept_gui",
    version=read("pept_gui", "VERSION"),
    description="Awesome pept_gui created by dwerner95",
    url="https://github.com/dwerner95/pept-GUI/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="dwerner95",
    packages=find_packages(exclude=["tests", ".github"]),
    #package_dir={"": "pept_gui"},
    package_data={"ui": ["*.ui"]},
    include_package_data=True,
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": ["pept_gui = pept_gui.__main__:main"]
    },
    extras_require={"test": read_requirements("requirements-test.txt")},
)
