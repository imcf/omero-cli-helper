#!/usr/bin/env python

"""Helper script to generate commands to import a directory tree into OMERO.

Expects a directory hierarchy matching a valid OMERO layout (i.e. two levels of
directories, the top-level denoting the "Project", the lower level denoting the
"Dataset". Image files are only accepted inside the dataset directories.

The script will generate the OMERO CLI [1] commands to achieve the following
steps:

* Create a "Project" with the name of the corresponding directory.
* The same for every "Dataset" directory in each project.
* Link every dataset to its corresponding project parent.
* Import all files inside a dataset directory.
"""

import sys
import argparse
from os.path import join


def parse_arguments():
    """Parse commandline arguments."""
    argparser = argparse.ArgumentParser(description=__doc__)
    add = argparser.add_argument
    add('-f', '--filelist', type=file, required=True,
        help='File containing list of files to import')
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

    tree = {}
    for line in args.filelist.readlines():
        try:
            (project, dataset, image) = line.strip().split('/')
        except ValueError:
            print("WARNING, found irregular line: %s" % line)
            continue
        if not project in tree:
            tree[project] = {}
        if not dataset in tree[project]:
            tree[project][dataset] = []
        tree[project][dataset].append(image)

    args.filelist.close()

    for (proj, datasets) in tree.iteritems():
        print('PROJECT=$(%s obj new Project name="%s")' % (binomero, proj))
        print('echo ----------- $PROJECT: %s -----------' % proj)
        for dset in datasets.iterkeys():
            print('DATASET=$(%s obj new Dataset name="%s")' % (binomero, dset))
            print("echo '*** $DATASET: %s'" % dset)
            print('%s obj new ProjectDatasetLink parent=$PROJECT child=$DATASET' % binomero)
            for img in datasets[dset]:
                print('%s import "%s"' % (binomero, join(proj, dset, img)))



if __name__ == "__main__":
    sys.exit(main())
