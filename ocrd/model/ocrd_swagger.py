import codecs
import json

from ocrd.constants import (OCRD_TOOL_SCHEMA, OCRD_OAS3_SPEC)


GET_SCHEMA = {
    "description": "Get ocrd-tool.json",
    "produces": [],
    'responses': {
        "200": {
            'application/json': {
                "description": "Got ocrd-tool.json",
                "schema": OCRD_TOOL_SCHEMA,
            }
        }
    }
}

def _clone(obj):
    return json.loads(json.dumps(obj))

class OcrdSwagger(object):
    """
    Representing a Swagger OAI 3 schema.
    """

    @staticmethod
    def from_ocrd_tools(swagger_template, *ocrd_tool):
        if swagger_template is not None:
            with codecs.open(swagger_template, encoding='utf-8') as f:
                swagger = json.load(f)
        else:
            swagger = _clone(OCRD_OAS3_SPEC)
            del swagger['paths']['/ocrd/processor']
            del swagger['paths']['/ocrd/processor/jobid/{jobID}']

        # add all components
        if 'components' not in swagger:
            swagger['components'] = {}
        for component in OCRD_OAS3_SPEC['components']:
            swagger['components'][component] = OCRD_OAS3_SPEC['components'][component]

        # Add specific paths
        for ocrd_tool_file in ocrd_tool:
            with codecs.open(ocrd_tool_file, encoding='utf-8') as f:
                ocrd_json = json.load(f)
                for tool in ocrd_json['tools'].values():
                    OcrdSwagger._add_paths_for_tool(swagger, tool)

        return swagger

    @staticmethod
    def _add_paths_for_tool(swagger, tool):

        # e.g. /preprocessing/binarization/kraken-binarize
        p = "/%s" % (tool['executable'].replace('ocrd_', '').replace('ocrd-', ''))

        # parameters are optional
        if 'parameterSchema' not in tool:
            tool['parameterSchema'] = {}
        tool['parameterSchema'] = {
            'type': 'object',
            'properties': tool['parameterSchema']
        }

        if 'summary' not in tool:
            tool['summary'] = tool['description']

        # POST /ocrd/processor/{{ PROCESSOR_NAME }}
        post = _clone(OCRD_OAS3_SPEC['paths']['/ocrd/processor']['post'])
        post['tags'] = tool['categories']
        post['summary'] = tool['summary']
        post['description'] = tool['description']
        post['requestBody']['content']['multipart/form-data']['schema'] = _clone(OCRD_OAS3_SPEC['components']['schemas']['processors'])
        post['requestBody']['content']['multipart/form-data']['schema']['parameters'] = tool['parameterSchema']

        get_schema = _clone(GET_SCHEMA)
        get_schema['tags'] = tool['categories']
        swagger['paths'][p] = {
            'post': post,
            'get': get_schema
        }

        # GET /ocrd/processor/{{ PROCESSOR_NAME }}/{_id}
        get = _clone(OCRD_OAS3_SPEC['paths']['/ocrd/processor/jobid/{jobID}']['get'])
        get['tags'] = tool['categories']
        delete = _clone(OCRD_OAS3_SPEC['paths']['/ocrd/processor/jobid/{jobID}']['delete'])
        delete['tags'] = tool['categories']
        swagger['paths']["%s/{_id}" % p] = {
            'delete': delete,
            'get': get
        }
