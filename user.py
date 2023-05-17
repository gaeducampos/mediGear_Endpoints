from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import uuid
from pydantic.generics import GenericModel
from typing import List
import requests
import json
from typing import Generic, TypeVar
from typing import Optional
from uuid import UUID
from enum import Enum


class User(BaseModel):
    id: int
    username: str
    email: str
    provider: str
    confirmed: bool
    blocked: bool
    createdAt: str
    updatedAt: str
    fullName: str


class OrderTotal(BaseModel):
    id: str
    html: str
    total: float

    def __hash__(self) -> int:
        return hash((self.id, self.html, self.total))

    def __eq__(self, other: 'OrderTotal') -> bool:
        if isinstance(other, OrderTotal):
            return (self.id, self.html, self.total) == (other.id, other.html, other.total)
        return False


class InvoiceData(BaseModel):
    id: str
    html: str

    def __hash__(self):
        return hash((self.id, self.html))

    def __eq__(self, other):
        if not isinstance(other, InvoiceData):
            return False
        return self.id == other.id and self.html == other.html
