# Copyright (c) 2021, Sanjeesh and contributors
# For license information, please see license.txt

import frappe
import json
import requests
import string
import base64
from random import choice
from frappe.model.document import Document


class Customer(Document):
    pass

@frappe.whitelist()
def update_customer_points():
    try:
        url = 'http://88.201.64.7:4059/api/v1/Customer'
        response = requests.get(url)
        customers = response.json()
        for customer in customers:
            user = frappe.db.sql("""SELECT name from `tabUser` where email =%s or username=%s""", (
                customer["email"], customer["cpr"]), as_dict=True)
            if user:
                data = frappe.db.sql(
                    """Select name from tabCustomer where customer =%s""", user[0]["name"], as_dict=True)
                if data:                    
                    new_user_doc2 = frappe.get_doc('Customer', data[0]["name"])
                    new_user_doc2.points = customer["points"]
                    new_user_doc2.save(ignore_permissions=True)
                    frappe.db.commit()
            
        return {"status": "success"}        

    except BaseException as error:
        frappe.db.rollback()
        return {"status": "failed", "data": error}


@frappe.whitelist()
def update_customer():
    try:
        url = 'https://server.alsatermarket.com:4058/api/v1/Customer'
        response = requests.get(url)
        customers = response.json()
        for customer in customers:
            user = frappe.db.sql("""SELECT name from `tabUser` where email =%s or username=%s""", (
                customer["email"], customer["cpr"]), as_dict=True)
            if not user:
                # new user doc
                new_user_doc = frappe.get_doc({
                    'doctype': 'User',
                    'email': customer["email"],
                    'first_name': customer["customer_name"],
                    'username': customer["cpr"],
                    'new_password': customer["new_password"],
                    'send_welcome_email': 0,
                    'phone': customer["mobile_no"],
                    'mobile_no': customer["mobile_no"]
                })
                new_user_doc.insert(ignore_permissions=True)
                otp = generate_otp(4)
                # new customer doc
                new_user_doc1 = frappe.get_doc({
                    'doctype': 'Customer',
                    'customer': customer["email"],
                    'customer_name': customer["customer_name"],
                    'customer_name_arabic': customer["customer_name"],
                    'flat_no': customer["flat_no"],
                    'block_no': customer["block_no"],
                    'bldg_no': customer["bldg_no"],
                    'road_no': customer["road_no"],
                    'area_name': customer["area_name"],
                    'city_name': customer["city_name"],
                    'customer_status':  1 if customer["customer_status"] == 'Y' else 0,
                    'activation_code': otp,
                    'location': '006',
                    'points': customer["points"]
                })
                new_user_doc1.insert(ignore_permissions=True)
                # set user roles and api authentication

                user_details = frappe.get_doc("User", customer["email"])
                if not user_details.api_key:
                    api_key = frappe.generate_hash(length=15)
                    user_details.api_key = api_key

                api_secret = frappe.generate_hash(length=15)
                user_details.api_secret = api_secret
                user_details.flags.ignore_permissions = True
                user_details.add_roles("Ecommerce")
                user_details.user_type = 'Website User'
                user_details.save(ignore_permissions=True)

                frappe.db.commit()
            else:
                data = frappe.db.sql(
                    """Select name from tabCustomer where customer =%s""", user[0]["name"], as_dict=True)
                if data:
                    new_user_doc2 = frappe.get_doc('Customer', data[0]["name"])
                    new_user_doc2.points = customer["points"]
                    new_user_doc2.customer_status = 1 if customer["customer_status"] == 'Y' else 0
                    new_user_doc2.save(ignore_permissions=True)
                    frappe.db.commit()
        return {"status": "success"}
    except BaseException as error:
        frappe.db.rollback()
        return {"status": "failed", "data": error}


@frappe.whitelist(allow_guest=True)
def generate_otp(digits=4):
    chars = string.digits
    random = ''.join(choice(chars) for _ in range(digits))
    return random
