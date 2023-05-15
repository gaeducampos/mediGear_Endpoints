from product import *
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
from typing import Dict


class ProductData(BaseModel):
    data: Product


class OrderDetailIdAttributes(BaseModel):
    quantity: int
    createdAt: str
    updatedAt: str
    publishedAt: str
    product: ProductData


class OrderDetailIdInfo(BaseModel):
    id: int
    attributes: OrderDetailIdAttributes


class OrderDetailsId(BaseModel):
    data: OrderDetailIdInfo
    meta: Dict = {}
