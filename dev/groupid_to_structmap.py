#!/usr/bin/env python

from os.path import isfile
from sys import argv

from ocrd.model import OcrdMets

fname = argv[1]
if not isfile(fname):
    raise "File not found %s" % fname
mets = OcrdMets(filename=fname)

# pylint: disable=protected-access
for f in mets.find_files():
    if not f.pageId:
        groupid = f._el.get('GROUPID')
        if groupid:
            del f._el.attrib['GROUPID']
        else:
            groupid = "FIXME"
            print("!! File %s has neither GROUPID nor mets:fptr in the PHYSICAL structMap" % f.url)
        print("Setting page of %s to %s" % (f.ID, groupid))
        f.pageId = groupid

with open(fname, 'wb') as out:
    out.write(mets.to_xml(xmllint=True))
