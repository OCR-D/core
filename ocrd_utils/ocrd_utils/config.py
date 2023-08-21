"""
Most behavior of OCR-D is controlled via command-line flags or keyword args.
Some behavior is global or too cumbersome to handle via explicit code and
better solved by using environment variables.

OcrdConfigBase is a base class to make this more streamlined, to be subclassed
in the `ocrd` package for the actual values
"""

class OcrdConfigVariable():

    def __init__(self, name, description, parse_fn=str):
        self.name = name
        self.description = description
        self.parse_fn = parse_fn

class OcrdConfigBase():
    pass
