from os import environ
from json import loads
from time import sleep
from typing import Optional, Union
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Response, Body, status


app = FastAPI(title=" *** REST STUB (default) *** ", version="1.1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.atlassian.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StubItem(BaseModel):
    status: int
    body: Union[dict, list] = None


stubs: dict[str, StubItem] = {}
requests: list[dict] = []
timeout: int = int(environ.get('TIMEOUT'))


@app.get("/stubs")
async def watch_stubs():
    return stubs


@app.put("/define_stub")
async def create_stub(url: str, body: StubItem):
    stubs[url] = body
    return {"url": url, "body": body}


@app.get("/stub/{endpoint:path}")
@app.put("/stub/{endpoint:path}")
@app.post("/stub/{endpoint:path}")
@app.patch("/stub/{endpoint:path}")
@app.delete("/stub/{endpoint:path}")
@app.options("/stub/{endpoint:path}")
async def call_stub(endpoint: str,
                    request: Request,
                    response: Response,
                    body=Body(default=None, media_type="text/plain")):
    for _ in range(timeout*5):
        if endpoint in stubs:
            response.status_code = stubs[endpoint].status
            requests.append({"endpoint": endpoint,
                             "params": request.query_params,
                             "method": request.method,
                             "headers": request.headers,
                             "body": await request.body()})
            return stubs[endpoint].body
        else:
            sleep(0.2)
    response.status_code = status.HTTP_404_NOT_FOUND
    return {"message": f"stub for [ {endpoint} ] was not defined!\n"
                       f"waiting with timeout [ {timeout} ] sec."}


@app.delete("/stubs")
async def delete_all_stubs():
    stubs.clear()
    return 'removing all stubs is successful!'


@app.get("/requests")
async def watch_requests():
    return requests


@app.get("/request/{endpoint:path}")
async def get_last_request_for_endpoint(endpoint: str,
                                        response: Response,
                                        fetch: Optional[str] = None):
    lst: list = [rec for rec in requests if rec["endpoint"] == endpoint]
    if len(lst) != 0:
        last = lst[-1]
        if fetch:
            if fetch == 'body':
                try:
                    return loads(last[fetch])
                except ValueError as e:
                    return last[fetch]
            return last[fetch]
        return last
    response.status_code = status.HTTP_404_NOT_FOUND
    return f'has not any request for endpoint [ {endpoint} ]'


@app.delete("/requests")
async def delete_all_requests():
    requests.clear()
    return 'removing all requests is successful'
