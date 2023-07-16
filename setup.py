from setuptools import setup, find_packages

with open("Readme.md") as f:
    content = f.read()


setup(
    name="miauw-base-service",
    version="1.2.0",
    author="cheetahbyte",
    author_email="contact@cheetahbyte.dev",
    description="base service & worker class for miauw-social",
    long_description=content,
    long_description_content_type = "text/markdown",
    packages=find_packages(),
    py_modules="base_service",
)