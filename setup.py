from setuptools import setup, find_packages

setup(
    name="nyx-security",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # No external dependencies required
    ],
    entry_points={
        "console_scripts": [
            "nyx-security=nyx_security.cli:main",
        ],
    },
    author="Your Name",
    author_email="tajinro381kamado@gmail.com",
    description="A Python security module for token management",
    keywords="security, token, encryption",
    python_requires=">=3.7",
)   