#!/usr/bin/env python

"""Helper script to generate commands to import a directory tree into OMERO.

Expects a directory hierarchy matching a valid OMERO layout (i.e. two levels of
directories, the top-level denoting the "Project", the lower level denoting the
"Dataset". Image files are only accepted inside the dataset directories.

The script will generate the OMERO CLI commands to achieve the following steps:

* Create a "Project" with the name of the corresponding directory.
* The same for every "Dataset" directory in each project.
* Link every dataset to its corresponding project parent.
* Import all files inside a dataset directory.
"""

from __future__ import print_function

import sys
import argparse
from os import walk
from os.path import join, sep


def parse_arguments():
    """Parse commandline arguments."""
    argparser = argparse.ArgumentParser(description=__doc__)
    add = argparser.add_argument
    add('-t', '--tree', type=str, required=True,
        help='Root of directory tree to be imported.')
    add('--omeropath', type=str, default='~/OMERO.server',
        help='Full path to your OMERO base directory.')
    # add('-v', '--verbosity', dest='verbosity',
    #     action='count', default=0)
    try:
        args = argparser.parse_args()
    except IOError as err:
        argparser.error(str(err))
    return args


def main():
    """Parse commandline arguments and build commands."""
    args = parse_arguments()
    binomero = join(args.omeropath, 'bin/omero')

    # assemble the tree structure representing the project/dataset/image
    # hierarchy to be imported into OMERO:
    tree = {}
    wrong = []
    for dirname, _, files in walk(args.tree):
        for fname in files:
            try:
                _, proj, dset, img = join(dirname, fname).split(sep)
            except ValueError:
                wrong.append(join(dirname, fname))
                continue
            if proj not in tree:
                tree[proj] = {}
            if dset not in tree[proj]:
                tree[proj][dset] = []
            tree[proj][dset].append(img)

    for proj, datasets in tree.iteritems():
        print('PROJ=$(%s obj new Project name="%s")' % (binomero, proj))
        print('echo ----------- $PROJ: %s -----------' % proj)
        for dset in datasets.iterkeys():
            print('DSET=$(%s obj new Dataset name="%s")' % (binomero, dset))
            print("echo '*** $DSET:'", dset)
            print('%s obj new ProjectDatasetLink parent=$PROJ child=$DSET'
                  % binomero)
            for img in datasets[dset]:
                print('%s import -d $DSET "%s"' % (binomero, join(proj, dset, img)))


# TODO: header for sudo-login:
"""
bin/omero login --sudo=<admin> <user>@localhost
bin/omero sessions group <group_name>
"""


if __name__ == "__main__":
    sys.exit(main())
