#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='geodjango-timezones',
    version='1.0',
    description='Models to store and scripts to load timezone shapefiles to be usable inside a GeoDjango application.',
    author='Adam Fast',
    author_email='',
    url='https://github.com/adamfast/geodjango_timezones',
    packages=find_packages(),
    package_data={
    },
    include_package_data=True,
    install_requires=['pytz'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
