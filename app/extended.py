import re
from os import environ
from time import sleep
from json import loads
from typing import Dict, Optional, Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Response, Body, status
from app.json_ops import validate_by_jsonpath, perform_replacement
from app.dto import DefaultStubItem, ExtendedStubItem, StubConfig


app = FastAPI(title=" *** REST STUB (extended) *** ", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.atlassian.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

stubs: Dict[str, StubConfig] = {}
requests: list[dict] = []
timeout: int = int(environ.get('TIMEOUT'))


@app.get("/stubs")
async def watch_stubs():
    return stubs


@app.put("/define_stub")
async def create_stub(url: str, body: Union[ExtendedStubItem, DefaultStubItem]):
    if url in stubs:
        if isinstance(body, DefaultStubItem):
            stubs[url].default = body
        if isinstance(body, ExtendedStubItem):
            stubs[url].extended.append(body)
    else:
        if isinstance(body, DefaultStubItem):
            stubs[url] = StubConfig(default=body, list_ext=[])
        if isinstance(body, ExtendedStubItem):
            stubs[url] = StubConfig(list_ext=[body])
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
    for _ in range(timeout * 5):
        if endpoint in stubs:

            incoming_rq = {"endpoint": endpoint,
                           "params": request.query_params,
                           "method": request.method,
                           "headers": request.headers,
                           "body": await request.body()}

            requests.append(incoming_rq)
            utf8_body = incoming_rq['body'].decode(encoding='utf-8')
            cur_config: StubConfig = stubs[endpoint]
            fallback_stub: DefaultStubItem = cur_config.default
            stubs_with_rules: list = [stub for stub in cur_config.extended if stub.rules]
            stubs_with_rules.reverse()

            def prepare_answer(stub):
                if stub.headers:
                    response.headers.update(perform_replacement(stub.headers, utf8_body, incoming_rq['headers']))
                response.status_code = stub.status
                return perform_replacement(stub.body, utf8_body, incoming_rq['headers'])

            for stb in stubs_with_rules:
                try:
                    if stb.rules.allowedMethods:
                        assert incoming_rq['method'] in stb.rules.allowedMethods
                    if stb.rules.regexForBody:
                        assert bool(re.search(pattern=stb.rules.regexForBody, string=utf8_body))
                    if stb.rules.jPath:
                        validate_by_jsonpath(search='inBody',    dom=stb.rules.jPath, target=utf8_body)
                        validate_by_jsonpath(search='inParams',  dom=stb.rules.jPath, target=incoming_rq['params'])
                        validate_by_jsonpath(search='inHeaders', dom=stb.rules.jPath, target=incoming_rq['headers'])
                except Exception as exc: continue
                return prepare_answer(stub=stb)

            if fallback_stub is not None:
                return prepare_answer(stub=fallback_stub)

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
