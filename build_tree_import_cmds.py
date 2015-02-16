#!/usr/bin/env python

from os.path import join

BIN_OMERO = '~/OMERO.server/bin/omero'

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
    print('PROJECT=$(%s obj new Project name="%s")' % (BIN_OMERO, project))
    print('echo ----------- $PROJECT: %s -----------' % project)
    for dataset in datasets.iterkeys():
        print('DATASET=$(%s obj new Dataset name="%s")' % (BIN_OMERO, dataset))
        print("echo '*** $DATASET: %s'" % dataset)
        print('%s obj new ProjectDatasetLink parent=$PROJECT child=$DATASET' % BIN_OMERO)
        for image in datasets[dataset]:
            print('%s import "%s"' % (BIN_OMERO, join(project, dataset, image)))

