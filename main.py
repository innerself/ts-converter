import datetime
import json
from typing import Any, Annotated
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Query, Response, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')


class CustomJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return json.dumps(content, indent=2).encode("utf-8")


async def parse_ts(ts: int | None = None,
                   tz: str | None = Query(default='Europe/Moscow', max_length=50)) -> dict:
    content = {'message': 'Hello!'}
    dt_fmt = '%Y-%m-%d %H:%M:%S %z'
    if ts is not None:
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        content = {
            'timestamp': ts,
            'result': {
                'UTC': dt.strftime(dt_fmt),
                tz: dt.astimezone(ZoneInfo(tz)).strftime(dt_fmt),
            }
        }
    return content


@app.get("/", response_class=HTMLResponse)
@app.get("/timestamp/", response_class=HTMLResponse)
async def root(request: Request, content: Annotated[dict, Depends(parse_ts)]):
    return templates.TemplateResponse(
        request=request, name='index.html', context={'content': content},
    )


@app.get('/profiling/', response_class=HTMLResponse)
async def profiling(request: Request):
    return templates.TemplateResponse(request=request, name='profiling.html')


@app.get('/api/timestamp/', response_class=CustomJSONResponse)
async def api_root(content: Annotated[dict, Depends(parse_ts)]):
    return content
