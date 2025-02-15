"""The module responsible for custom exceptions."""

import json
from typing import Optional


class APIException(Exception):
    """The exception is for errors from third-party APIs."""

    def __init__(
        self,
        service_name: str,
        status_code: int,
        msg: Optional[str] = None,
        json_str: Optional[str] = None,
    ):
        """
        Init class.

        :param service_name: Name of API service.
        :param status_code: Status code.
        :param msg: Message from server.
        :param json_str: JSON from server.
        """
        self.service_name = service_name
        self.status_code = status_code
        self.msg = msg
        self.json_str = json_str

    def __str__(self) -> str:
        """Return str of exception."""
        res_str: str = f"Service: {self.service_name}, Status code: {self.status_code}"
        if self.msg:
            res_str += ", ".join((res_str, self.msg))
        if self.json_str:
            res_str += ", ".join((res_str, json.dumps(self.json_str, indent=2)))

        return res_str
