# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from doc import project

with open('README.rst') as f:
    long_desc = f.read()

setup(
    name=project.name,
    version=project.version,
    url=project.url,
    download_url=project.download_url,
    project_urls=project.project_urls,
    license=project.license,
    author=project.author,
    description=project.description,
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    keywords=project.keywords,
    platforms='any',
    python_requires='>=3',
    packages=find_packages(),
    include_package_data=True,
    install_requires= ['Sphinx'],
    namespace_packages=['sphinxnotes'],
)