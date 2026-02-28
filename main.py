from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
import logging

from urls_db import Urls


app = FastAPI()


logging.basicConfig(
    level = logging.INFO,
    format = 
"%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers = [
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("shorty")


def get_db():
    db = Urls()
    return db


class URLRequest(BaseModel):
    url: HttpUrl


@app.post("/shorten")
async def shorten(request: Request, url_req: URLRequest, db = Depends(get_db)):
    large = str(url_req.url)
    short = db.create_pair(large=large)
    logger.info(f"Shorten: {large} --> {short}")
    base_url = str(request.base_url)
    return {"short_url": f"{base_url}{short}"}


@app.get("/{code}")
async def redirect_from_short(code: str, request: Request, db: Urls = Depends(get_db)):
    url = db.get_url(short=code)
    if not url:
        logger.warning(f"Попытка перехода по несуществующему коду: {code}")
        raise HTTPException(status_code=404, detail="Ссылка отсутствует")
    client = getattr(request, "client", None)
    host = getattr(client, "host", "unknown") if client else "unknown"
    logger.info(f"Redirect: {code} --> {url} | IP: {host}")
    return RedirectResponse(url=url, status_code=307)
