import logging

def getLogger(*args, **kwargs):
    return logging.getLogger(*args, **kwargs)

logging.basicConfig(level=logging.DEBUG)
#  logging.getLogger('ocrd.resolver').setLevel(logging.INFO)
logging.getLogger('ocrd.resolver.download_to_directory').setLevel(logging.INFO)
logging.getLogger('ocrd.resolver.add_files_to_mets').setLevel(logging.INFO)
logging.getLogger('PIL').setLevel(logging.INFO)
