import datetime
import json
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Query, Response

app = FastAPI()


class CustomJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        return json.dumps(content, indent=2).encode("utf-8")


@app.get("/", response_class=CustomJSONResponse)
async def root(ts: int | None = None,
               tz: str | None = Query(default='Europe/Moscow', max_length=50)):
    content = {'message': 'Hello!'}
    dt_fmt = '%Y-%m-%d %H:%M:%S %z'
    if ts is not None:
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        content = {
            'UTC': dt.strftime(dt_fmt),
            tz: dt.astimezone(ZoneInfo(tz)).strftime(dt_fmt),
        }

    return content
