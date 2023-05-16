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
    html: str
    total: float
