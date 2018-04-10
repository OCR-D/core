import codecs
import json

from ocrd.constants import (
    OCRD_TOOL_SCHEMA,
    OCRD_OAS3_SKELETON,
    OCRD_OAS3_REQUEST_BODY,
    OCRD_OAS3_GET_PROCESS
)


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
            swagger = _clone(OCRD_OAS3_SKELETON)
        for ocrd_tool_file in ocrd_tool:
            with codecs.open(ocrd_tool_file, encoding='utf-8') as f:
                ocrd_json = json.load(f)
                for tool in ocrd_json['tools']:
                    OcrdSwagger._add_paths_for_tool(swagger, tool)
        return swagger

    @staticmethod
    def _add_paths_for_tool(swagger, tool):
        p = "/%s/%s" % (tool['step'], tool['binary'].replace('ocrd_', ''))

        if 'parameterSchema' not in tool:
            tool['parameterSchema'] = {}
        tool['parameterSchema'] = {
            'type': 'object',
            'properties': tool['parameterSchema']
        }
        requestBody = _clone(OCRD_OAS3_REQUEST_BODY)
        requestBody['content']['multipart/mixed']['schema']['properties']['parameterJson']['schema'] = tool['parameterSchema']

        response201 = {
            "description": "Successfully ran '%s'" % tool['binary'],
            "headers": {
                "Location": {
                    "type": "string",
                    "format": "uri",
                    "description": "URL of the resulting METS"
                },
            },
        }

        if 'summary' not in tool:
            tool['summary'] = tool['description']

        swagger['paths'][p] = {
            "post": {
                "tags": tool["tags"],
                "summary": tool["summary"],
                "description": tool["description"],
                "requestBody": requestBody,
                "responses": {
                    "201": response201,
                }
            },
        }

        GET_PROCESS = _clone(OCRD_OAS3_GET_PROCESS)
        GET_PROCESS['get']['tags'] = tool['tags']
        swagger['paths']["%s/{_id}" % p] = GET_PROCESS
