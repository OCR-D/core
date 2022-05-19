from fastapi import FastAPI, APIRouter, status, Depends

from ocrd import Processor
from ocrd.server.models.ocrd_tool import OcrdTool

tags_metadata = [
    {
        'name': 'Processing',
        'description': 'OCR-D processing and processors'
    }
]

app = FastAPI(
    openapi_tags=tags_metadata
)


def get_processor() -> Processor | None:
    # If the processor is loaded into memory before, use it
    if hasattr(app, 'processor'):
        return app.processor

    # The server was started from a non-Python processor
    return None


router = APIRouter()


@router.get('/', tags=['Processing'], status_code=status.HTTP_200_OK, summary='Get information about this processor.',
            response_model=OcrdTool)
async def get_processor(processor: Processor = Depends(get_processor)):
    if processor:
        return processor.ocrd_tool
    return app.processor_info


app.include_router(router, prefix='/processor')
