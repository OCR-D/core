import json
import yaml

import click

from ocrd import OcrdSwagger

# ----------------------------------------------------------------------
# ocrd generate-swagger
# ----------------------------------------------------------------------

@click.command('generate-swagger', help="Generate Swagger schema from ocrd-tool.json files")
@click.option('-S', '--swagger-template', help="Swagger template to add operations to. Use builtin if not specified.")
@click.option('-T', '--ocrd-tool', multiple=True, help="ocrd-tool.json file to generate from. Repeatable")
@click.option('-f', '--format', help="Format to generate, JSON or YAML", type=click.Choice(['JSON', 'YAML']), default='JSON')
def generate_swagger_cli(swagger_template, ocrd_tool, **kwargs):
    swagger = OcrdSwagger.from_ocrd_tools(swagger_template, *ocrd_tool)
    if kwargs['format'] == 'YAML':
        print(yaml.dump(swagger))
    else:
        print(json.dumps(swagger, indent=2))
