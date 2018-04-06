# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('Readme.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='Batch generator',
    version='0.1.0',
    description='Package to handle batch systems on clusters.',
    long_description=readme,
    classifiers=[
        'Development status :: 1 - Alpha',
        'License :: CC-By-SA2.0',
        'Programming Language :: Python',
    ],
    author='Corentin Cadiou',
    author_email='contact@cphyc.me',
    url='https://github.com/cphyc/batch_generator',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'appdirs',

    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'batch = batch_generator.__main__:main'
        ]
    },
)
