import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyise",
    version="0.0.3",
    author="Bugra Onal",
    author_email="onalbugra@gmail.com",
    description="This is a Python wrapper for Xilinx ISE with the added functionality of batch synthesis and simulation. The console output of batch operations are logged.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bugraonal/PyISE",
    project_urls={
        "Bug Tracker": "https://github.com/bugraonal/PyISE/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
