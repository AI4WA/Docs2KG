import os
import re

from setuptools import find_packages, setup


def read_requirements():
    with open("requirements.txt", "r") as req:
        content = req.read()
        requirements = content.split("\n")
    return requirements


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    # then for all images inside the markdown
    # add the url https://github.com/AI4WA/Docs2KG/blob/main to the image path
    images = re.findall(r"!\[.*\]\((.*)\)", long_description)

    for image in images:
        if "http" in image:
            continue
        long_description = long_description.replace(
            image, "https://raw.githubusercontent.com/AI4WA/Docs2KG/main/" + image
        )

# get the version from GITHUB_REF_NAME
version = os.getenv("GITHUB_REF_NAME", None)
if not version:
    version = "v0.0.0"

setup(
    name="Docs2KG",
    author="AI4WA",
    author_email="admin@ai4wa.com",
    description="Unified Knowledge Graph Construction from Heterogeneous Documents Assisted by Large Language Models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=version,
    packages=find_packages(),  # Adjust the location where setuptools looks for packages
    include_package_data=True,  # To include other types of files specified in MANIFEST.in or found in your packages
    install_requires=read_requirements(),
    python_requires=">=3.8",  # Specify your Python version compatibility
    classifiers=[
        # Classifiers help users find your project by categorizing it
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        # license: GNU LESSER GENERAL PUBLIC LICENSE
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        # topic
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    url="https://docs2kg.ai4wa.com",
    project_urls={
        "Source": "https://github.com/AI4WA/Docs2KG",
    },
)
