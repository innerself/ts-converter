import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/")
async def root(ts: int | None = None,
               tz: str | None = Query(default='Europe/Moscow', max_length=50)):
    if ts is not None:
        dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        return {
            'UTC': dt.strftime('%Y-%m-%d %H:%M:%S %z'),
            tz: dt.astimezone(ZoneInfo(tz)),
        }
    return {'message': 'Hello!'}
