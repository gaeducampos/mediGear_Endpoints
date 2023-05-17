import os
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import io
import uuid
from order import *
from user import *
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
                            orderDetails=final_order_details,
                            location=order.attributes.location)

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
                            orderDetails=final_order_details,
                            location=order.attributes.location)

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
                            orderDetails=final_order_details,
                            location=order.attributes.location
                        )

                        user_order.append(final_order)

    json_compatible_item_data = jsonable_encoder(user_order)
    return JSONResponse(content=json_compatible_item_data)


@app.get("/medigear-iosApp/get/orders/completed")
async def get_user_order_completed(user_id: int):
    json_compatible_item_data = jsonable_encoder(await get_active_orders(user_id=user_id))
    return JSONResponse(content=json_compatible_item_data)


async def get_user_data(user_id):
    user_get_url = f"http://localhost:1338/api/users/{user_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(user_get_url, headers=headers) as response:
            user_data_reponse = await response.json()
            return user_data_reponse


@app.get("/medigear-iosApp/get/pdf")
async def generate_order_pdf(user_id: int):
    response = await get_active_orders(user_id=user_id)
    user_data_reponse = await get_user_data(user_id=user_id)
    if len(response) == 0:
        raise HTTPException(
            status_code=404, detail="Not found")
    else:
        user_data = User.parse_obj(user_data_reponse)
        order_data_response = response

        # full invoice data
        invoice_data = ""

        # detail invoice data (products, price, name etc...)
        invoice_order_details_data = ""
        total = 0.0
        # each invoice details goes here
        invoice_details = []

        # each full invoice info goes here
        invoice_data_set = []

        for order_info in order_data_response:
            for order_details in order_info.orderDetails:
                total += float(
                    order_details.product.data.attributes.price) * order_details.quantity
                invoice_order_details_data += f"""
                 <tr>
                    <td style="vertical-align: top"><br />{order_details.quantity}</td>
                     <td style="vertical-align: top"><br />{order_details.product.data.attributes.name}</td>
                    <td style="vertical-align: top"><br />${order_details.product.data.attributes.price}</td>
                     <td style="vertical-align: top"><br />$0.00</td>
                    <td style="vertical-align: top"><br />$0.00</td>
                    <td style="vertical-align: top"><br />${total}</td>
                </tr>
                
                """
            order_total = OrderTotal(
                id=order_info.orderReference, html=invoice_order_details_data, total=total)

            invoice_details.append(order_total)
            invoice_order_details_data = ""
            total = 0.0

        logging.debug(len(invoice_details))
        for orders_info in order_data_response:
            for invoices in orders_info.orderDetails:
                invoice_data += f"""
                    <div class="container">
                        <table class="header" style="text-align: left; width: 457px; height: 144px" border="1" cellpadding="2"
                        cellspacing="2">
                        <tbody>
                            <tr>
                            <td style="vertical-align: top">MEDIGEAR S.A. DE C.V. <br /></td>
                            <td style="vertical-align: top" width="35%">C.FACTURA</td>
                            </tr>
                            <tr>
                            <td style="vertical-align: top">
                                Adquisicion de Equipos Medicos y Más
                            </td>
                            <td style="vertical-align: top"><br />No. {orders_info.id}</td>
                            </tr>
                            <tr>
                            <td style="vertical-align: top">
                                Tel. 2258-9635; * 71289031 <br />
                            </td>
                            <td style="vertical-align: top">NIT: 0614-011523-135-0</td>
                            </tr>
                            <tr>
                            <td style="vertical-align: top">ventas@medigear.com.sv</td>
                            <td style="vertical-align: top">NRC: 316585-5</td>
                            </tr>
                        </tbody>
                        </table>
                        <table style="text-align: left; width: 457px; height: 95px" border="1" cellpadding="2" cellspacing="2">
                        <tbody>
                            <tr>
                            <td style="vertical-align: top" width="15% ">Cliente:</td>
                            <td style="vertical-align: top" width="40%">{user_data.fullName}</td>
                            <td style="vertical-align: top" width="15% ">Fecha:</td>
                            <td style="vertical-align: top"><br />{orders_info.deliveryTime}</td>
                            </tr>
                            <tr>
                            <td style="vertical-align: top" width="10% ">Direccion:</td>
                            <td colspan="3" rowspan="1"><br />{orders_info.location}</td>
                        </tbody>
                        </table>

                        <table style="text-align: left; width: 456px; height: 284px" border="1" cellpadding="2" cellspacing="2">
                        <tbody>
                            <tr>
                            <td style="vertical-align: top">CANT<br /></td>
                            <td style="vertical-align: top">Producto<br /></td>
                            <td style="vertical-align: top">PRECIO c/u<br /></td>
                            <td style="vertical-align: top">Ventas no Sujetas<br /></td>
                            <td style="vertical-align: top">Ventas Exentas<br /></td>
                            <td style="vertical-align: top">Ventas Afectas<br /></td>
                            </tr>

                            {invoices.html}

                            <tr>
                            <td colspan="4" rowspan="4" style="vertical-align: top"><br /></td>
                            <td style="vertical-align: top">SUMAS<br /></td>
                            <td style="vertical-align: top"><br />${invoices.total}</td>
                            </tr>
                            <tr>
                            <td style="vertical-align: top">IVA RET<br /></td>
                            <td style="vertical-align: top"><br />$0.00</td>
                            </tr>
                            <tr>
                            <td style="vertical-align: top">SUBTOTAL<br /></td>
                            <td style="vertical-align: top"><br />${invoices.total}</td>
                            </tr>
                            <tr>
                            <td style="vertical-align: top">VENTA n/s<br /></td>
                            <td style="vertical-align: top"><br />$0.00</td>
                            </tr>
                            <tr>
                            <td colspan="3" rowspan="1" style="vertical-align: top">
                                Dado en <br />
                            </td>
                            <td style="vertical-align: top"><br /></td>
                            <td style="vertical-align: top">VENTA Ex<br /></td>
                            <td style="vertical-align: top"><br />$0.00</td>
                            </tr>
                            <tr>
                            <td colspan="3" rowspan="1" style="vertical-align: top">
                                Manufacturado por <br />
                            </td>
                            <td style="vertical-align: top"><br /></td>
                            <td style="vertical-align: top">Total <br /></td>
                            <td style="vertical-align: top"><br />${orders_info.total}</td>
                            </tr>
                            
                        </tbody>
                        </table>
                        <br />
                        <div class="newPage"></div>
                    </div>
                """
            invoice_data_set.append(invoice_data)
            invoice_data = ""

        # invoice_obj = InvoiceData(
        #     id=orders_info.orderReference, html=invoice_data)

    # invoice_non_repeted_content = ""
    # unique_items = list({item.id: item for item in invoice_data_set}.values())

    logging.debug(len(invoice_data_set))
    htmls_generated = []
    html = ""
    for invoice_info in invoice_data_set:
        html += f"""
                <!DOCTYPE html class="newhtml">
                    <html lang="en">
                    <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Document</title>
                    </head>

                    <body>
                        {invoice_info}
                    </body>

                    </html>
                """
        htmls_generated.append(html)
        html = ""

    for html in htmls_generated:
        return create_pdf(html_content=html)


def create_pdf(html_content):
    # Find the tag that determines the page break
    page_break_tag = '<div class="newPage"></div>'

    # Split the HTML content by the page break tag
    content_pages = html_content.split(page_break_tag)

    # Create a list to store the paths of temporary HTML files
    temp_html_files = []

    try:
        # Iterate over the content pages
        for i, page_content in enumerate(content_pages):
            # Create a temporary HTML file for each page
            temp_html_file = f'temp_page_{i}.html'
            temp_html_files.append(temp_html_file)

            # Append the page content to the temporary HTML file
            with open(temp_html_file, 'w') as file:
                file.write(page_content)

        # Convert each temporary HTML file to a PDF page
        pdfkit.from_file(temp_html_files, 'user-invoice.pdf')
        with open("user-invoice.pdf", "rb") as file:
            pdf_contents = file.read()

        # encode the contents as a base64 string
        pdf_base64 = base64.b64encode(pdf_contents).decode("utf-8")

        response = {}
        response["pdf"] = pdf_base64

        json_compatible_item_data = jsonable_encoder(response)
        return JSONResponse(content=json_compatible_item_data)

    finally:
        # Clean up the temporary HTML files
        for temp_html_file in temp_html_files:
            os.remove(temp_html_file)
