from click import option

def mets_find_options(f):
    for opt in  [
        option('-G', '--file-grp', help="fileGrp USE", metavar='FILTER'),
        option('-m', '--mimetype', help="Media type to look for", metavar='FILTER'),
        option('-g', '--page-id', help="Page ID", metavar='FILTER'),
        option('-i', '--file-id', help="ID", metavar='FILTER'),
    ]:
        opt(f)
    return f
