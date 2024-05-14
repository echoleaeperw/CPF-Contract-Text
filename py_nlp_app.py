import logging
import warnings

# 关闭paddle的警告
# warnings.filterwarnings("ignore")

import uvicorn
from fastapi import FastAPI

from ocr.views import ocr_router
from nlp.views import nlp_router
from page_index.views import page_index_router
from fastapi.staticfiles import StaticFiles
from app_tools.logger import Logger

log = Logger()

app = FastAPI()
app.include_router(ocr_router)
app.include_router(nlp_router)
app.include_router(page_index_router)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == '__main__':
    uvicorn.run('py_nlp_app:app',
                host='0.0.0.0',
                port=8088,
                # reload=True,
                log_config=log.get_logging_config(),
                workers=1)
