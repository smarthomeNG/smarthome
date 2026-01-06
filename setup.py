#!/usr/bin/env python3
import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_URL = ('https://github.com/smarthomeNG/smarthome/archive/v{}.zip'.format("1.6"))

PACKAGES = find_packages(exclude=['tests', 'tests.*'])

#REQUIRES = [
#    'requests>=2,<3',
#    'pyyaml>=3.11,<4',
#    'psutil',
#
#]
REQUIRES = [
]

setup(
    name='SmartHomeNG',
    version="1.6b",
    license='GPL',
    url='https://github.com/smarthomeNG/smarthome',
    download_url=DOWNLOAD_URL,
    author='',
    author_email='',
    description='Open-source home automation platform running on Python 3.',
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=REQUIRES,
    test_suite='tests',
    keywords=['home', 'automation'],
    entry_points={
        'console_scripts': [
            ''
        ]
    },
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Home Automation'
    ],
)
