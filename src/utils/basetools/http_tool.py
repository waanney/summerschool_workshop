"""
HTTP request and response handling module.

This module provides functionality for making HTTP requests with configurable
methods, headers, body types, and response parsing. It supports JSON, form data,
and raw body types with proper error handling and timeout management.
"""

from typing import Dict, Optional, Union
from enum import Enum
import json

from pydantic import BaseModel, Field
import requests


class BodyType(str, Enum):
    """Enum for HTTP request body types."""

    JSON = "json"
    FORM = "form"
    RAW = "raw"


class ResponseType(str, Enum):
    """Enum for HTTP response parsing types."""

    JSON = "json"
    TEXT = "text"
    BYTES = "bytes"


class HTTPMethod(str, Enum):
    """Enum for HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HttpRequest(BaseModel):
    """Input model for HTTP request configuration."""

    url: str = Field(..., description="Target URL for the HTTP request")
    method: HTTPMethod = Field(HTTPMethod.GET, description="HTTP method to use")
    headers: Optional[Dict[str, str]] = Field(
        None, description="HTTP headers to include"
    )
    params: Optional[Dict[str, str]] = Field(None, description="URL query parameters")
    body_type: BodyType = Field(BodyType.JSON, description="Type of request body")
    body: Optional[Union[Dict[str, str | int | float | bool], str, bytes]] = Field(
        None, description="Request body content"
    )
    response_type: ResponseType = Field(
        ResponseType.JSON, description="Expected response type"
    )
    timeout: int = Field(10, description="Request timeout in seconds")

    def model_post_init(self, __context) -> None:
        """
        Post-initialization hook to ensure the body is serialized correctly based on its type.

        This method automatically converts dictionary bodies to JSON strings when
        the body type is set to RAW.
        """
        if self.body_type == BodyType.RAW and isinstance(self.body, dict):
            object.__setattr__(
                self,
                "body",
                json.dumps(self.body, ensure_ascii=False),
            )


class HttpResponse(BaseModel):
    """Output model for HTTP response data."""

    status_code: int = Field(..., description="HTTP status code of the response")
    headers: Dict[str, str] = Field(..., description="Response headers")
    body: Union[Dict[str, str | int | float | bool | list | dict], str, bytes] = Field(
        ..., description="Response body content"
    )
    url: str = Field(..., description="Final URL after any redirects")
    elapsed_time: float = Field(..., description="Request duration in seconds")


def http_tool(req: HttpRequest) -> HttpResponse:
    """
    Execute an HTTP request with the specified configuration.

    This function performs HTTP requests using the requests library with support
    for different HTTP methods, body types, and response parsing. It handles
    JSON, form data, and raw body types with proper error handling.

    Args:
        req: HttpRequest object containing all request configuration

    Returns:
        HttpResponse: Object containing response data and metadata

    Raises:
        requests.RequestException: If the HTTP request fails
        requests.Timeout: If the request times out
        requests.ConnectionError: If unable to connect to the server
        ValueError: If request configuration is invalid
    """
    kwargs: Dict[
        str,
        Union[
            str,
            Dict[str, str],
            int,
            Union[Dict[str, str | int | float | bool], str, bytes],
        ],
    ] = {
        "url": str(req.url),
        "headers": req.headers,
        "params": req.params,
        "timeout": req.timeout,
    }

    # Handle request body based on method and body type
    if req.method in {HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH}:
        if req.body_type == BodyType.JSON:
            kwargs["json"] = req.body or {}
        elif req.body_type == BodyType.FORM:
            kwargs["data"] = req.body or {}
        else:  # RAW
            kwargs["data"] = req.body or b""
    elif req.body is not None:
        kwargs["data"] = req.body

    # Execute the request
    resp: requests.Response = requests.request(req.method.value, **kwargs)

    # Parse response based on response type
    parsed_body: Union[
        Dict[str, str | int | float | bool | list | dict], str, bytes
    ] = _parse_response_body(resp, req.response_type)

    return HttpResponse(
        status_code=resp.status_code,
        headers=dict(resp.headers),
        body=parsed_body,
        url=resp.url,
        elapsed_time=resp.elapsed.total_seconds(),
    )


def _parse_response_body(
    response: requests.Response, response_type: ResponseType
) -> Union[Dict[str, str | int | float | bool | list | dict], str, bytes]:
    """
    Parse response body based on the specified response type.

    Args:
        response: requests.Response object
        response_type: Type of response parsing to perform

    Returns:
        Union[Dict[str, str | int | float | bool | list | dict], str, bytes]: Parsed response body

    Raises:
        ValueError: If JSON parsing fails and fallback is not possible
    """
    if response_type == ResponseType.JSON:
        try:
            return response.json()
        except ValueError:
            # Fallback to text if JSON parsing fails
            return response.text
    elif response_type == ResponseType.TEXT:
        return response.text
    else:  # ResponseType.BYTES
        return response.content
