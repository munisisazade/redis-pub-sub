import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="redispubsub",
    version=__import__("redisrpc").VERSION,
    author="Munis Isazade",
    author_email="munisisazade@gmail.com",
    description="Redis RPC server for microservices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/munisisazade/redispubsub",
    install_requires=["redis"],
    extras_require={
        "redis": ["redis"]
    },
    platforms=['any'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
