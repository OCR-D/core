import click


@click.group('client')
def client_cli():
    """
    A client for interacting with the network modules
    """


@client_cli.group('discovery')
def client_cli_discovery():
    pass


@client_cli.group('workflow')
def client_cli_workflow():
    pass


@client_cli.group('workspace')
def client_cli_workspace():
    pass


@client_cli.group('processing')
def client_cli_processing():
    pass
