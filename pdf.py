import os
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import io
import uuid
from main import *
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
            # Header
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
                            <td style="vertical-align: top"><br />No. {order_info.id}</td>
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
                            <td style="vertical-align: top"><br />{order_info.deliveryTime}</td>
                            </tr>
                            <tr>
                            <td style="vertical-align: top" width="10% ">Direccion:</td>
                            <td colspan="3" rowspan="1"><br />{order_info.location}</td>
                        </tbody>
                        </table>
            """
            for order_details in order_info.orderDetails:
                # Details n
                total += float(
                    order_details.product.data.attributes.price) * order_details.quantity
                invoice_data += f"""
                 <tr>
                    <td style="vertical-align: top"><br />{order_details.quantity}</td>
                     <td style="vertical-align: top"><br />{order_details.product.data.attributes.name}</td>
                    <td style="vertical-align: top"><br />${order_details.product.data.attributes.price}</td>
                     <td style="vertical-align: top"><br />$0.00</td>
                    <td style="vertical-align: top"><br />$0.00</td>
                    <td style="vertical-align: top"><br />${total}</td>
                </tr>

                """
            # order_total = OrderTotal(
            #     id=order_info.orderReference, html=invoice_order_details_data, total=total)

            # invoice_details.append(order_total)
            total = 0.0
         # Footer
        invoice_data += f"""
        <tr>
            <td colspan="4" rowspan="4" style="vertical-align: top"><br /></td>
                <td style="vertical-align: top">SUMAS<br /></td>
                            <td style="vertical-align: top"><br />${order_info.total}</td>
                            </tr>
                            <tr>
                            <td style="vertical-align: top">IVA RET<br /></td>
                            <td style="vertical-align: top"><br />$0.00</td>
                            </tr>
                            <tr>
                            <td style="vertical-align: top">SUBTOTAL<br /></td>
                            <td style="vertical-align: top"><br />${order_info.total}</td>
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
                            <td style="vertical-align: top"><br />${order_info.total}</td>
                            </tr>
                            
                        </tbody>
                        </table>
                        <br />
                        <div class="newPage"></div>
                    </div>
        """
        # page
        invoice_details.append(invoice_data)
        invoice_data = ""

    # pages_array

    logging.debug(len(invoice_details))
    htmls_generated = []
    html = ""
    for invoice_info in invoice_details:
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
