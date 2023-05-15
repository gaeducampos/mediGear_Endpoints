import os
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import io
import uuid
from order import *
from orderDetails import *
from product import *
from pydantic.generics import GenericModel
from typing import List
import requests
import json
from typing import Generic, TypeVar
from typing import Optional
from uuid import UUID
from typing import Dict, Any
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import asyncio
import base64
import aiohttp

import pdfkit
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import logging


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.DEBUG)

DataT = TypeVar('DataT')

token = "dfdea37a44142d2e50cca7bbe80a959a5b4724a5581942cb5c43515eb8a556367306c7ae748545ec55dc59a9f49a701b9f9a54333cf6f43471684b7d7e4ade57552290a18e7e666bf6925f9030cab50ea1e15fb6f7763e79719941e0826b8b6359734d5a967c80595b13bf45c4113a62708fe05d895a0fa224d9d896a12ba781"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

fast_api_headers = {
    "Content-Type": "application/json"
}


# get the current working directory
cwd = os.getcwd()

# define the path to the file relative to the current directory
file_path = "/invoice.html"

# get the absolute path of the file
absolute_path = os.path.abspath(file_path)

# get the relative path of the file from the current working directory
invoice_relative_path = os.path.relpath(absolute_path, cwd)


# End points callers


@app.get("/medigear-iosApp")
async def read_root():
    return {"Hello": "World"}


@app.post("/medigear-iosApp/product/update")
async def update_products(cart_products: List[CartProduct]):
    if cart_products != None and len(cart_products) > 0:
        for cart_product in cart_products:
            product_id = str(cart_product.product.id)
            put_url = f"http://localhost:1338/api/products/{product_id}"
            payload = {"data": {
                "amount": cart_product.product.attributes.amount - cart_product.quantity}}
            response = requests.put(put_url, json=payload, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, detail=response.text)
        return Response(status_code=204)
    else:
        return Response(status_code=403)


@app.get("/medigear-iosApp/get/orders/pending")
async def get_user_order_pending(user_id: int):
    user_order = []
    get_url = f"http://localhost:1338/api/orders?filters[userId][$eq]={user_id}&populate=*"

    async with aiohttp.ClientSession() as session:
        async with session.get(get_url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status, detail=response.text)
            else:
                order_data_response = await response.json()
                order = Order.parse_obj(order_data_response)

                for order in order.data:
                    final_order_details = []
                    for orderDetails in order.attributes.order_details.data:
                        get_url_orderDetails = f"http://localhost:1338/api/order-details/{orderDetails.id}?populate=*"
                        async with session.get(get_url_orderDetails, headers=headers) as order_details_response:
                            if order_details_response.status != 200:
                                raise HTTPException(
                                    status_code=order_details_response.status, detail=order_details_response.text)
                            else:
                                order_details_data = await order_details_response.json()
                                order_details = OrderDetailsId.parse_obj(
                                    order_details_data)

                                if order.attributes.status == StatusOrder.pending:
                                    final_order_details.append(FinalOrderDetails(
                                        product=order_details.data.attributes.product,
                                        quantity=order_details.data.attributes.quantity)
                                    )
                    if order.attributes.status == StatusOrder.pending:
                        final_order = FinalOrder(
                            id=uuid.uuid4(),
                            orderReference=order.attributes.orderReference,
                            status=order.attributes.status,
                            total=order.attributes.total,
                            deliveryTime=order.attributes.deliveryTime,
                            orderDetails=final_order_details)

                        user_order.append(final_order)

    json_compatible_item_data = jsonable_encoder(user_order)
    return JSONResponse(content=json_compatible_item_data)


async def get_active_orders(user_id):
    user_order = []
    get_url = f"http://localhost:1338/api/orders?filters[userId][$eq]={user_id}&populate=*"

    async with aiohttp.ClientSession() as session:
        async with session.get(get_url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status, detail=response.text)
            else:
                order_data_response = await response.json()
                order = Order.parse_obj(order_data_response)

                for order in order.data:
                    final_order_details = []
                    for orderDetails in order.attributes.order_details.data:
                        get_url_orderDetails = f"http://localhost:1338/api/order-details/{orderDetails.id}?populate=*"
                        async with session.get(get_url_orderDetails, headers=headers) as order_details_response:
                            if order_details_response.status != 200:
                                raise HTTPException(
                                    status_code=order_details_response.status, detail=order_details_response.text)
                            else:
                                order_details_data = await order_details_response.json()
                                order_details = OrderDetailsId.parse_obj(
                                    order_details_data)

                                if order.attributes.status == StatusOrder.complete:
                                    final_order_details.append(FinalOrderDetails(
                                        product=order_details.data.attributes.product,
                                        quantity=order_details.data.attributes.quantity)
                                    )
                    if order.attributes.status == StatusOrder.complete:
                        final_order = FinalOrder(
                            id=uuid.uuid4(),
                            orderReference=order.attributes.orderReference,
                            status=order.attributes.status,
                            total=order.attributes.total,
                            deliveryTime=order.attributes.deliveryTime,
                            orderDetails=final_order_details)

                        user_order.append(final_order)
    return user_order


@app.get("/medigear-iosApp/get/orders/active")
async def get_user_order_active(user_id: int):
    user_order = []
    get_url = f"http://localhost:1338/api/orders?filters[userId][$eq]={user_id}&populate=*"

    async with aiohttp.ClientSession() as session:
        async with session.get(get_url, headers=headers) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status, detail=response.text)
            else:
                order_data_response = await response.json()
                order = Order.parse_obj(order_data_response)

                for order in order.data:
                    final_order_details = []
                    for orderDetails in order.attributes.order_details.data:
                        get_url_orderDetails = f"http://localhost:1338/api/order-details/{orderDetails.id}?populate=*"
                        async with session.get(get_url_orderDetails, headers=headers) as order_details_response:
                            if order_details_response.status != 200:
                                raise HTTPException(
                                    status_code=order_details_response.status, detail=order_details_response.text)
                            else:
                                order_details_data = await order_details_response.json()
                                order_details = OrderDetailsId.parse_obj(
                                    order_details_data)

                                if order.attributes.status == StatusOrder.active:
                                    final_order_details.append(FinalOrderDetails(
                                        product=order_details.data.attributes.product,
                                        quantity=order_details.data.attributes.quantity)
                                    )
                    if order.attributes.status == StatusOrder.active:
                        final_order = FinalOrder(
                            id=uuid.uuid4(),
                            orderReference=order.attributes.orderReference,
                            status=order.attributes.status,
                            total=order.attributes.total,
                            deliveryTime=order.attributes.deliveryTime,
                            orderDetails=final_order_details)

                        user_order.append(final_order)

    json_compatible_item_data = jsonable_encoder(user_order)
    return JSONResponse(content=json_compatible_item_data)


@app.get("/medigear-iosApp/get/orders/completed")
async def get_user_order_completed(user_id: int):
    json_compatible_item_data = jsonable_encoder(await get_active_orders(user_id=user_id))
    return JSONResponse(content=json_compatible_item_data)


@app.get("/medigear-iosApp/get/pdf")
async def generate_order_pdf(user_id: int):
    response = await get_active_orders(user_id=user_id)
    if len(response) == 0:
        raise HTTPException(
            status_code=404, detail="Not found")
    else:
        order_data_response = response
        logging.debug(order_data_response)

        order_data = ""
        for orders_info in order_data_response:
            order_data += f"""
                <h3>ID Mandamiento de pago mh.gob.sv: {orders_info.id}</h3>
                <h3>Numero de referencia con MediGear: #{orders_info.orderReference }</h3>
                <h3>Total: ${orders_info.total}</h3>
                <h3>Fecha de entrega: {orders_info.deliveryTime}</h3>
                <h1>====================================================</h1>
            """

        html = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Document</title>
                </head>

                <body>
                    <h1>Comprobante de ordernes:</h1>
                    <h2>Lista de ordenes completadas</h2>
                    <h1>====================================================</h1>
                    {order_data}
                </body>

                </html>
            """

        with open("invoice.html", "w") as file:
            file.write(html)

        logging.debug("HTML")
        pdfkit.from_file('invoice.html', 'user-invoice.pdf')

        logging.debug("PDF")
        # get the current working directory
        cwd = os.getcwd()

        # define the path to the file relative to the current directory
        file_path = "/user-invoice.pdf"

        # get the absolute path of the file
        user_absolute_path = os.path.abspath(file_path)

        # get the relative path of the file from the current working directory
        user_invoice_relative_path = os.path.relpath(user_absolute_path, cwd)

        # read the contents of the PDF file
        with open("user-invoice.pdf", "rb") as file:
            pdf_contents = file.read()

        # encode the contents as a base64 string
        pdf_base64 = base64.b64encode(pdf_contents).decode("utf-8")

        response = {}
        response["pdf"] = pdf_base64
        logging.debug(pdf_base64)

    json_compatible_item_data = jsonable_encoder(response)
    logging.debug("response")
    return JSONResponse(content=json_compatible_item_data)
