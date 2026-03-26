from __future__ import annotations

from typing import Literal
from dataclasses import dataclass, field
import uuid
from enum import Enum

from result import Err as ResultError 
from result import Ok as ResultOk 
from result import Result, is_err, is_ok


class Err(ResultError): 
    def is_err(self) -> Literal[True]: 
        return True 
    def is_ok(self) -> Literal[False]: 
        return False

class Ok(ResultOk): 
    def is_err(self) -> Literal[False]: 
        return False
    def is_ok(self) -> Literal[True]: 
        return True

class ErrorType(Enum): 
    INFRA= "INFRA"
    CLIENT= "CLIENT"

@dataclass(frozen=True, kw_only=True)
class Error: 
    id: str = field(default_factory=lambda: uuid.uuid4().hex) # for tracing
    code: int 
    message: str
    reason: str | dict | Exception | Error = ""
    retryable: bool = False
    error_type: ErrorType = ErrorType.CLIENT

    def to_dict(self) -> dict: 
        return {
            "err_id": self.id,
            "err_code": self.code,
            "message": self.message,
            "reason": self.reason,
        }
    
    def public(self) -> dict: 
        return {
            "err_id": self.id,
            "err_code": self.code,
            "message": self.message,
        }

    def __repr__(self) -> str: 
        return f"Error(id={self.id}, code={self.code}, message={self.message}, reason={self.reason})"

class Return: 
    @staticmethod
    def ok(value: Any) -> Ok: 
        return Ok(value)

    @staticmethod
    def err(error: Error) -> Err: 
        return Err(error)    

__all__ = ["Error", "Ok", "Err", "Return", "is_err", "is_ok", "Result"]