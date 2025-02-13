from setuptools import setup, find_packages

setup(
    name="first_court",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "rich",
        "python-dotenv"
    ]
)
