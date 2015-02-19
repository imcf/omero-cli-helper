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

BLKMARK = '################################################################'
DSHMARK = '----------------------------------------------------------------'
STRMARK = '****************************************************************'

HEADER = '''#!/bin/sh

set -x
set -e

BINOMERO="%s"
DTSTRING=$(date +%%F_%%H%%M)

omero_import_file() {
    PROJ=$(cat _cur_project)
    DSET=$(cat _cur_dset)
    echo "$1" > _cur_filename
    "$BINOMERO" import -d $DSET "$1"
    echo "$1" >> _done_filenames
    rm _cur_filename
}

#### uncomment these lines and adjust admin/user/group:
# "$BINOMERO" logout
# "$BINOMERO" login --sudo=<admin> -u <user> -s localhost
# "$BINOMERO" sessions group <group_name>
'''


def parse_arguments():
    """Parse commandline arguments."""
    argparser = argparse.ArgumentParser(description=__doc__)
    add = argparser.add_argument
    add('-t', '--tree', type=str, required=True,
        help='Root of directory tree to be imported.')
    add('--omeropath', type=str, default='$HOME/OMERO.server',
        help='Full path to your OMERO base directory.')
    # add('-v', '--verbosity', dest='verbosity',
    #     action='count', default=0)
    try:
        args = argparser.parse_args()
    except IOError as err:
        argparser.error(str(err))
    return args


def print_wrong_items(wronglist):
    """Print the list of invalid file items in the directory tree."""
    if len(wronglist) == 0:
        return
    print('', file=sys.stderr)
    print(BLKMARK, file=sys.stderr)
    print('# WARNING: found incorrect items in dir tree!', file=sys.stderr)
    print(BLKMARK, file=sys.stderr)
    for item in wronglist:
        print(item, file=sys.stderr)
    print(BLKMARK, file=sys.stderr)


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

    # print the script header with functions and global vars
    print(HEADER % binomero)

    for proj, datasets in tree.iteritems():
        print('\necho\necho "', BLKMARK, BLKMARK, '"\necho\n')
        print('PROJ_NAME="%s"' % proj)
        print('"$BINOMERO" obj new Project name="$PROJ_NAME" > _cur_project')
        print('PROJ=$(cat _cur_project)')
        print('echo "', DSHMARK, '$PROJ: $PROJ_NAME', DSHMARK, '"')
        for dset in datasets.iterkeys():
            print('DSET_NAME="%s"' % dset)
            print('"$BINOMERO" obj new Dataset name="$DSET_NAME" > _cur_dset')
            print('DSET=$(cat _cur_dset)')
            print('echo "', STRMARK, '$DSET: $DSET_NAME"')
            print('"$BINOMERO" obj new ProjectDatasetLink',
                  'parent=$PROJ child=$DSET')
            for img in datasets[dset]:
                print('omero_import_file "%s"' % join(proj, dset, img))
            print('echo "$DSET_NAME" >> _done_dsets_names')
            print('cat _cur_dset >> _done_dsets_ids')
            print('rm _cur_dset')

        print('echo "$PROJ_NAME" >> _done_projects_names')
        print('cat _cur_project >> _done_projects_ids')
        print('rm _cur_project')

    print_wrong_items(wrong)



if __name__ == "__main__":
    sys.exit(main())
