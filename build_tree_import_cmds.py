#!/usr/bin/env python

import sys
import argparse

from os.path import join


def parse_arguments():
    """Parse commandline arguments."""
    argparser = argparse.ArgumentParser(description=__doc__)
    add = argparser.add_argument
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
    args = parse_arguments()
    binomero = join(args.omeropath, 'bin/omero')
    fh = open('files.txt')

    tree = {}

    for line in fh.readlines():
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

    fh.close()

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
