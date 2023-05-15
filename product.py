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


class Pagination(BaseModel):
    page: int
    pageSize: int
    pageCount: int
    total: int


class MedicalMinistrationAttributes(BaseModel):
    createdAt: str
    updatedAt: str
    publishedAt: str
    img: str
    name: str
    products: None


class MedicalMinistration(BaseModel):
    id: int
    attributes: MedicalMinistrationAttributes


class ProductDimensions(BaseModel):
    width: str
    height: str
    depth: str
    weight: str


class ProductAttributes(BaseModel):
    name: str
    description: str
    serial_number: str
    createdAt: str
    updatedAt: str
    publishedAt: str
    dimensions: ProductDimensions
    price: str
    currency: str
    date_added: str
    amount: int
    isAvailable: bool
    img: str


class Product(BaseModel):
    id: int
    attributes: ProductAttributes


class CartProduct(BaseModel):
    id: UUID
    product: Product
    quantity: int


class MedicalMinistrationAttributes(BaseModel):
    createdAt: str
    updatedAt: str
    publishedAt: str
    img: str
    name: str
    products: Optional[None] = None


class MedicalMinistration(BaseModel):
    id: int
    attributes: MedicalMinistrationAttributes
