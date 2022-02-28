from setuptools import setup, find_packages
import dictdot

description = dictdot.__doc__
long_description = description + "\n\n" + dictdot.dictdot.__doc__

setup(
    name="dictdot",
    version="1.3.1",
    author="nchz",
    url="https://github.com/nchz/dictdot",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    packages=find_packages(),
)
