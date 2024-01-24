from click import option

def mets_find_options(f):
    for opt in  [
        option('-G', '--file-grp', help="fileGrp USE", metavar='FILTER'),
        option('-m', '--mimetype', help="Media type to look for", metavar='FILTER'),
        option('-g', '--page-id', help="Page ID", metavar='FILTER'),
        option('-i', '--file-id', help="ID", metavar='FILTER'),
        option('-q', '--include-file-grps', 'include_fileGrp', help="fileGrps to include", default=[], multiple=True),
        option('-Q', '--exclude-file-grps', 'exclude_fileGrp', help="fileGrps to exclude", default=[], multiple=True),
    ]:
        opt(f)
    return f
