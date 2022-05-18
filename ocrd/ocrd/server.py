from fastapi import FastAPI, Depends

from ocrd import Processor
from ocrd_utils import initLogging

initLogging()

app = FastAPI(
    title='OCR-D Processor',
    description='Processing Server',
    version='0.0.1'
)


def get_processor() -> Processor | None:
    # If the processor is loaded into memory before, use it
    if hasattr(app, 'processor'):
        return app.processor

    # The server was started from a non-Python processor
    return None


@app.get('/')
async def hello(processor: Processor = Depends(get_processor)):
    if processor:
        return processor.ocrd_tool
    return {'message': 'No processor object'}
