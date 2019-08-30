import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="redispubsub",
    version=__import__("redispubsub").VERSION,
    author="Munis Isazade",
    author_email="munisisazade@gmail.com",
    description="Redis RPC server for microservices",
    long_description=long_description,
    license='MIT',
    url="https://github.com/munisisazade/redispubsub",
    install_requires=["redis"],
    platforms=['any'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
