from product import *
from orderDetails import *
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


class StatusOrder(Enum):
    pending = "s1"
    active = "s2"
    complete = "s3"


class OrderDetailsAttributes(BaseModel):
    quantity: int
    createdAt: str
    updatedAt: str
    publishedAt: str


class SingleOrderDetail(BaseModel):
    id: int
    attributes: OrderDetailsAttributes


class OrderDetails(BaseModel):
    data: List[SingleOrderDetail]


class OrderAttributes(BaseModel):
    total: float
    location: str
    userId: int
    deliveryTime: str
    orderReference: str
    createdAt: str
    updatedAt: str
    status: Optional[StatusOrder] = None
    order_details: OrderDetails


class OrderInfo(BaseModel):
    id: int
    attributes: OrderAttributes


class Pagination(BaseModel):
    page: int
    pageSize: int
    pageCount: int
    total: int


class Meta(BaseModel):
    pagination: Pagination


class Order(BaseModel):
    data: List[OrderInfo]
    meta: Meta


class FinalOrderDetails(BaseModel):
    product: ProductData
    quantity: int


class FinalOrder(BaseModel):
    id: UUID
    orderReference: str
    status: StatusOrder
    total: float
    deliveryTime: str
    orderDetails: List[FinalOrderDetails]
