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

    for (project, datasets) in tree.iteritems():
        print('PROJECT=$(%s obj new Project name="%s")' % (binomero, project))
        print('echo ----------- $PROJECT: %s -----------' % project)
        for dataset in datasets.iterkeys():
            print('DATASET=$(%s obj new Dataset name="%s")' % (binomero, dataset))
            print("echo '*** $DATASET: %s'" % dataset)
            print('%s obj new ProjectDatasetLink parent=$PROJECT child=$DATASET' % binomero)
            for image in datasets[dataset]:
                print('%s import "%s"' % (binomero, join(project, dataset, image)))



if __name__ == "__main__":
    sys.exit(main())
