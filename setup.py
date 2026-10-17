from codecs import open
from os import path
from setuptools import find_packages, setup

from drafthorse import version

here = path.abspath(path.dirname(__file__))

try:
    # Get the long description from the relevant file
    with open(path.join(here, "README.rst"), encoding="utf-8") as f:
        long_description = f.read()
except:  # noqa
    long_description = ""

setup(
    name="drafthorse-ng",
    version=version,
    description="Python ZUGFeRD XML implementation",
    long_description=long_description,
    url="https://github.com/timounger/python-drafthorse-ng",
    author="Timo Unger",
    license="Apache License",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    keywords="xml banking sepa",
    install_requires=["lxml", "pypdf"],
    extras_require={"schematron": ["saxonche"]},
    packages=find_packages(include=["drafthorse", "drafthorse.*"]),
    include_package_data=True,
)
