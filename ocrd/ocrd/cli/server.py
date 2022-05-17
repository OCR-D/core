from fastapi import FastAPI

app = FastAPI(
    title='OCR-D Processor',
    description='Processing Server',
    version='0.0.1',
)


@app.get('/')
async def hello():
    return {'message': 'Hello World!'}
