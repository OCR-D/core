def cache_key_from_url(url):
    return re.replace(url, '[^A-Za-z0-9]', '', 'g')

class ResolverCache(object):
    """
    Cache of downloads, based on URL.
    """

    def __init__(self, directory):
        self.directory = directory
        if not os.path.isdir(self.directory):
            raise Exception("Cache directory does not exist: %s" % (self.directory))

    def get(url):
        filename = os.path.join(self.directory, cache_key_from_url(url))
        if os.path.exists():
            return filename
        else:
            return None

    def put(url, content):
        filename = os.path.join(self.directory, cache_key_from_url(url))
        with open(filename, 'wb') as outfile:
            outfile.write(content)
        return filename

