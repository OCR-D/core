import codecs
import json

from ocrd.constants import OCRD_TOOL_SCHEMA, SWAGGER_TEMPLATE

PARAM_METS_URL = {
    "name": "mets_url",
    "in": "formData",
    "type": "string",
    "description": "XML holding all information of the digitized document. All references of the images are available via fileGrp section (ID=\"OCR-D-IMG\") inside the METS document."
    }

PARAM_PARAMETER_JSON = {
    "name": "parameter_json",
    "in": "formData",
    "description": "Parameter in JSON",
    "type": "string"
    }

OP_GET_OCRD_TOOL_JSON = {
    "description": "Get ocrd-tool.json",
    "produces": ['application/json'],
    'responses': {
        "200": {
            "description": "Got ocrd-tool.json",
            "schema": OCRD_TOOL_SCHEMA,
            }
        }
    }

HEADER_LOCATION_METS_URL = {
    "type": "string",
    "format": "uri",
    "description": "URL of the resulting METS"
}

def _clone(obj):
    return json.loads(json.dumps(obj))

class OcrdSwagger(object):
    """
    Representing a Swagger OAI 2 schema.
    """

    @staticmethod
    def from_ocrd_tools(swagger_template, *ocrd_tool):
        if swagger_template is not None:
            with codecs.open(swagger_template, encoding='utf-8') as f:
                swagger = json.load(f)
        else:
            swagger = _clone(SWAGGER_TEMPLATE)
        for ocrd_tool_file in ocrd_tool:
            with codecs.open(ocrd_tool_file, encoding='utf-8') as f:
                ocrd_json = json.load(f)
                for tool in ocrd_json['tools']:
                    p = "/%s/%s" % (tool['step'], tool['binary'].replace('ocrd_', ''))
                    swagger['paths'][p] = {
                        "post": {
                            "description": tool['description'],
                            "parameters": [
                                _clone(PARAM_METS_URL),
                                _clone(PARAM_PARAMETER_JSON),
                            ],
                            "responses": {
                                "201": {
                                    "description": "Successfully ran '%s'" % tool['binary'],
                                    "headers": {
                                        "Location": _clone(HEADER_LOCATION_METS_URL),
                                    },
                                    "schema": {},
                                }
                            }
                        },
                        "get": _clone(OP_GET_OCRD_TOOL_JSON)
                    }
        return swagger
