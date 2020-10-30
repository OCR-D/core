from .report import ValidationReport

class OcrdGdsCollector(ValidationReport):

    def __init__(self, filename=None, messages=None):
        super().__init__()
        self.filename = filename
        if messages is None:
            self.warnings = []
        else:
            self.warnings = messages

    def add_message(self, msg):
        self.add_warning(msg)

    def get_messages(self):
        return self.warnings

    def clear_messages(self):
        self.warnings = []

    def print_messages(self):
        for msg in self.warnings:
            print("Warning: {}".format(msg))

    def write_messages(self, outstream):
        for msg in self.warnings:
            outstream.write("Warning: {}\n".format(msg))

class GdsCollector(OcrdGdsCollector):
    pass
