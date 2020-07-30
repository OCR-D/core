class OcrdGdsCollector(object):

    def __init__(self, messages=None):
        print('GdsCollector.__init__', self)
        if messages is None:
            self.messages = []
        else:
            self.messages = messages

    def add_message(self, msg):
        self.messages.append(msg)

    def get_messages(self):
        return self.messages

    def clear_messages(self):
        self.messages = []

    def print_messages(self):
        for msg in self.messages:
            print("Warning: {}".format(msg))

    def write_messages(self, outstream):
        for msg in self.messages:
            outstream.write("Warning: {}\n".format(msg))

class GdsCollector(OcrdGdsCollector):
    pass
