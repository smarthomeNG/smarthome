#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab

"""
This script can create a backup by combining the configuration files from ``etc``, ``items`` and ``scenes`` to a ``tar.gz`` file.

Alternatively it can restore the configuration files from a previous backup.
"""

import tarfile
import zipfile
import os
import argparse

# for tarfile fix, maybe not necessary as os is already imported...
from os.path import abspath, realpath, dirname, join as joinpath
# also for tarfile fix. As no logging is defined, this skips files instead of halting...
import sys


class BackupAndRestore:
    def __init__(self):
        self.files = []
        self.workdir = os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-2])
        self.workdir_len = len(self.workdir.split(os.path.sep))-1
        self.backupdirs = ['etc','items','scenes']
        self.exclude_files = ('.default','.gitignore')
        self.verbose=False
        self.overwrite=False

    def backup(self, outfile, include=None, exclude=None):
        if os.path.isfile(outfile) and self.overwrite == False:
            raise ValueError("Outputfile exists "+ outfile)
        if exclude != None:
            self.backupdirs = set(self.backupdirs) - set(exclude)
        if include != None:
            self.backupdirs = self.backupdirs+include
        if self.verbose: print (self.backupdirs)
        for path in self.backupdirs:
            self.get_files(os.path.join(self.workdir, path))
        if self.verbose: print (self.files)
        tar = tarfile.open(outfile, "w:gz")
        for name in self.files:
            tar.add(name, filter=self.change_fileinfo)
        tar.close()

    def get_files(self,apath):
        if not os.path.exists(apath):
            raise ValueError(" Directory not found! '" + apath + "'")

        for root, dirnames, filenames in os.walk(apath):
            for filename in filenames:
                if not filename.lower().endswith(self.exclude_files):
                    self.files.append(os.path.join(root, filename))

    def change_fileinfo(self,tarinfo):
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = "root"
        newname = os.path.sep.join(tarinfo.name.split(os.path.sep)[self.workdir_len:])
        if self.verbose: print(newname)
        tarinfo.name = newname
        return tarinfo

    def restore(self, afile, outdir, selector=None):

        # added and adjusted fix for CVE-2007-4559) from https://stackoverflow.com/questions/10060069/safely-extract-zip-or-tar-using-python/10077309#10077309
        resolved = lambda x: realpath(abspath(x))

        def badpath(path, base):
            # joinpath will ignore base if path is absolute
            return not resolved(joinpath(base, path)).startswith(base)

        def badlink(info, base):
            # Links are interpreted relative to the directory containing the link
            tip = resolved(joinpath(base, dirname(info.name)))
            return badpath(info.linkname, base=tip)

        def safemembers(members):
            base = resolved(".")

            for finfo in members:
                if badpath(finfo.name, base):
                    print(f'{finfo.name} is blocked (illegal path)', file=sys.stderr)
                elif finfo.issym() and badlink(finfo, base):
                    print(f'{finfo.name} is blocked: hard link to {finfo.linkname}', file=sys.stderr)
                elif finfo.islnk() and badlink(finfo, base):
                    print(f'{finfo.name} is blocked: symlink to {finfo.linkname}', file=sys.stderr)
                else:
                    yield finfo

        readmode = None
        extractor = None
        afilelow = afile.lower()
        if (afilelow.endswith("tar.gz") or afilelow.endswith("tgz")):
            extractor = tarfile.open
            readmode = "r:gz"
        elif (afilelow.endswith("tar")):
            extractor = tarfile.open
            readmode = "r:"
        elif (afilelow.endswith("zip")):
            extractor = zipfile.ZipFile
            readmode = "r"
        elif (afilelow.endswith("bz2") or afilelow.endswith("tbz")):
            extractor = tarfile.open
            readmode = "r:bz2"
        if extractor != None:
            tar = extractor(afile, readmode)
            try:
                tar.extractall(path=outdir)
            finally: 
                tar.close() 
        else:
            raise ValueError("Unsupported file type: " + afile)

if __name__ == '__main__':
    bar = BackupAndRestore()
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-b', '--backup', action='store_true', help='create a config backup')
    group.add_argument('-r', '--restore',  action='store', help='restore a backup',metavar='dir')
    parser.add_argument('--backupfile', action='store', help='name for outputfile (default: backup.tar.gz)',metavar='file', default='backup.tar.gz')
    parser.add_argument('--include', nargs='+', action='store', help='include directory to backup',metavar='dir')
    parser.add_argument('--exclude', nargs='+', action='store', help='exclude directory from backup (only for etc,items,scenes)',metavar='dir')
    parser.add_argument('-v','--verbose', action='store_true', help='generate more output', default=False)
    parser.add_argument('--overwrite', action='store_true', help='allways overwrite existing files', default=False)
    args = parser.parse_args()
    try:
        if args.verbose:
            print (args)
            bar.verbose=True
        if args.overwrite:
            bar.overwrite=True
        if args.backup:
            bar.backup(outfile=args.backupfile, include=args.include, exclude=args.exclude)
        if args.restore != None:
            bar.restore(afile=args.backupfile, outdir=args.restore)
    except ValueError as e:
        print("")
        print(e)
        print("")
        parser.print_help()
        exit(1)   
