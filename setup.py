from setuptools import setup, find_packages


description = "Python dict accessible by dot."

with open("README.md") as f:
    long_description = f.read()

setup(
    name="dictdot",
    version="1.5.0",
    author="nchz",
    url="https://github.com/nchz/dictdot",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    packages=find_packages(),
)
