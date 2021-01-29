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
        'Environment :: Plugins',
        'Framework :: Sphinx',
        'Framework :: Sphinx :: Extension',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Documentation :: Sphinx',
        'Topic :: System :: Shells',
        'Topic :: Text Processing :: Markup :: reStructuredText',
        'Topic :: Utilities',
    ],
    keywords=project.keywords,
    platforms='any',
    python_requires='>=3',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'khufu= sphinxnotes.khufu:main',
        ],
    },
    install_requires= [
        'Sphinx',
        'langdetect',
        'jieba',
        'python-pinyin',
        'pyxdg',
        'tabulate',
        'summa',
        'stopwordsiso',
        'wcwidth'
    ],
    namespace_packages=['sphinxnotes'],
)