from fastapi import FastAPI

from ocrd_utils import initLogging, getLogger

initLogging()
log = getLogger('ocrd.cli.server')

app = FastAPI(
    title='OCR-D Processor',
    description='Processing Server',
    version='0.0.1',
)


@app.get('/')
async def hello():
    return {'message': 'Hello World!'}
