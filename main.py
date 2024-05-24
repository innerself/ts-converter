import datetime
import json
from pathlib import Path
from textwrap import dedent
from typing import Any, Annotated
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Query, Response, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import PlainTextResponse

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
    css_path = request.app.url_path_for('static', path='/profdebug.css')
    js_path = '/static-gen/profiling.js'
    return templates.TemplateResponse(
        request=request,
        name='profdebug.html',
        context={'css_path': css_path, 'js_path': js_path},
    )


@app.get('/debugging/', response_class=HTMLResponse)
async def debugging(request: Request):
    css_path = request.app.url_path_for('static', path='/profdebug.css')
    js_path = '/static-gen/debugging.js'
    return templates.TemplateResponse(
        request=request,
        name='profdebug.html',
        context={'css_path': css_path, 'js_path': js_path},
    )


@app.get('/static-gen/profiling.js', response_class=PlainTextResponse)
async def profiling_js(request: Request):
    first_row_text = dedent("""
        `import time
        from loguru import logger
        logger.debug('========================================')
        pf_t1 = time.monotonic()`
    """)

    consequent_row_text = dedent("""
        `pf_t${currentLine} = time.monotonic()
        logger.debug('========== pf_t${currentLine - 1} ==========')
        logger.debug(f'Time from pf_t${currentLine - 1}: {pf_t${currentLine} - pf_t${currentLine - 1}}')
        logger.debug(f'Time from start: {pf_t${currentLine} - pf_t1}')`
    """)

    base_js = Path(__file__).parent.joinpath('static', 'profdebug.js')
    with open(base_js) as init_file:
        code = init_file.read()
        code = code.replace("'%%storage_list_name%%'", "'profilingList'")
        code = code.replace("'%%first_row_text%%'", first_row_text)
        code = code.replace("'%%consequent_row_text%%'", consequent_row_text)

    return code


@app.get('/static-gen/debugging.js', response_class=PlainTextResponse)
async def debugging_js(request: Request):
    main_text = dedent(f"""
        `logger.debug('${{currentLine}}${{`-${{currentLine}}`.repeat(13)}}-${{currentLine}}')`
    """)

    prefixes = '\n', '`'
    first_row_text = dedent(f"""
        `from loguru import logger
        {main_text.removeprefix(prefixes[0]).removeprefix(prefixes[1])}
    """)

    base_js = Path(__file__).parent.joinpath('static', 'profdebug.js')
    with open(base_js) as init_file:
        code = init_file.read()
        code = code.replace("'%%storage_list_name%%'", "'debuggingList'")
        code = code.replace("'%%first_row_text%%'", first_row_text)
        code = code.replace("'%%consequent_row_text%%'", main_text)

    return code


@app.get('/api/timestamp/', response_class=CustomJSONResponse)
async def api_root(content: Annotated[dict, Depends(parse_ts)]):
    return content
