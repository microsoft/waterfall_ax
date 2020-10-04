import setuptools

with open("waterfall_ax/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="waterfall_ax-test3", 
    version="0.0.1",
    author="Yaran Fan",
    author_email="yarfan.fan@gmail.com",
    description="Create waterfall charts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/microsoft/waterfall_ax",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)