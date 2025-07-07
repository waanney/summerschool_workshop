from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Union
import json
from enum import Enum
import requests
class BodyType(str, Enum):
    JSON = "json"
    FORM = "form"
    RAW  = "raw"

class ResponseType(str, Enum):
    JSON  = "json"
    TEXT  = "text"
    BYTES = "bytes"

class HTTPMethod(str, Enum):
    GET    = "GET"
    POST   = "POST"
    PUT    = "PUT"
    DELETE = "DELETE"
    PATCH  = "PATCH"
    HEAD   = "HEAD"
    OPTIONS = "OPTIONS"


class HttpRequest(BaseModel):
    url: str
    method: HTTPMethod = HTTPMethod.GET
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, str]] = None

    body_type: BodyType = BodyType.JSON
    body: Optional[Union[Dict[str, Any], str, bytes]] = None

    response_type: ResponseType = ResponseType.JSON
    timeout: int = 10


    def model_post_init(self, __context):
        """
        Nếu body_type == RAW, mà body là dict ⇒ chuyển sang chuỗi JSON.
        """
        if self.body_type == BodyType.RAW and isinstance(self.body, dict):
            object.__setattr__(
                self,
                "body",
                json.dumps(self.body, ensure_ascii=False),
            )



class HttpResponse(BaseModel):
    status_code: int
    headers: Dict[str, str]
    body: Union[Dict[str, Any], str, bytes]
def http_tool(req: HttpRequest) -> HttpResponse:




    kwargs: Dict[str, Any] = {
        "url": str(req.url),
        "headers": req.headers,
        "params": req.params,
        "timeout": req.timeout,
    }

    if req.method in {HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH}:
        if req.body_type == BodyType.JSON:
            kwargs["json"] = req.body or {}
        elif req.body_type == BodyType.FORM:
            kwargs["data"] = req.body or {}
        else:  # RAW
            kwargs["data"] = req.body or b""
    elif req.body is not None:

        kwargs["data"] = req.body

    # 2. Gửi request
    resp = requests.request(req.method.value, **kwargs)

    # 3. Parse kết quả
    if req.response_type == ResponseType.JSON:
        try:
            parsed_body: Union[Dict[str, Any], str, bytes] = resp.json()
        except ValueError:
            parsed_body = resp.text  # fallback
    elif req.response_type == ResponseType.TEXT:
        parsed_body = resp.text
    else:
        parsed_body = resp.content  # bytes

    return HttpResponse(
        status_code=resp.status_code,
        headers=dict(resp.headers),
        body=parsed_body,
    )