#!/usr/bin/env python3

from distutils.core import setup, Extension


def main():
    module = Extension('rrdtool', sources=['rrdtool.c'],
                       libraries=['rrd'])

    kwargs = dict(
        name='python3-rrdtool',
        version='0.1.1',
        description='rrdtool bindings for Python 3',
        keywords=['rrdtool'],
        author='Marcus Popp, Christian Jurk, Hye-Shik Chang',
        author_email='marcus@popp.mx',
        ext_modules=[module]
    )

    setup(**kwargs)

if __name__ == '__main__':
    main()
