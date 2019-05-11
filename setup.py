#!/usr/bin/env python3
import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
DOWNLOAD_URL = ('https://github.com/{}.zip'.format("1.1"))

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
    version="1.3",
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
        'Operating System :: Linux',
        'Programming Language :: Python :: 3.4',
        'Topic :: Home Automation'
    ],
)
