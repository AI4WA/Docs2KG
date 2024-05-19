from setuptools import setup, find_packages


def read_requirements():
    with open('requirements.txt', 'r') as req:
        content = req.read()
        requirements = content.split('\n')
    return requirements


setup(
    name="Docs2KG",
    version="0.1.0",
    packages=find_packages(where="Docs2KG"),  # Adjust the location where setuptools looks for packages
    package_dir={"": "Docs2KG"},  # Map the package names to the 'src' directory
    include_package_data=True,  # To include other types of files specified in MANIFEST.in or found in your packages
    install_requires=read_requirements(),
    python_requires='>=3.6',  # Specify your Python version compatibility
    classifiers=[
        # Classifiers help users find your project by categorizing it
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # Adjust the license accordingly
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
