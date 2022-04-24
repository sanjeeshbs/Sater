
import frappe
import json
import base64
import requests
import string
from random import choice


@frappe.whitelist(allow_guest=True)
def request_password():
    try:

        user_details = json.loads(frappe.request.data)
        user = frappe.db.sql("""SELECT * from `tabUser` where (email =%s or username=%s) and mobile_no like%s""",
                             (user_details["username"], user_details["username"], "%{0}%".format(user_details["mobile"])), as_dict=True)
        if not user:
            return {"status": "failed", "error": 'User Not Found'}
        else:
            customer = frappe.db.sql(
                """Select name,customer_status from tabCustomer where customer =%s""", user[0]["email"], as_dict=True)
            if not customer:
                return {"status": "failed", "error": 'User Not Found'}
            else:
                if customer[0]["customer_status"] == 1:
                    doc = frappe.get_doc('User', user[0]["name"])
                    new_password = generate_otp(5)
                    doc.new_password = new_password
                    doc.save(ignore_permissions=True)

                    if user[0]["mobile_no"]:
                        send_sms(user[0]["mobile_no"],
                                 f'Your login password: {new_password}')
                    return {"status": "success", "data": doc.name}
                else:
                    doc = frappe.get_doc('Customer', customer[0]["name"])
                    otp = generate_otp(4)
                    doc.activation_code = otp
                    doc.save(ignore_permissions=True)
                    frappe.db.commit()
                    if user[0]["mobile_no"]:
                        send_sms(user[0]["mobile_no"],
                                 f'Activation code: {otp}')

                    return {"status": "activate", "error": 'User Not Active'}
    except BaseException as error:
        return {"status": "failed", "error": error}


@frappe.whitelist(allow_guest=True)
def get_shop_locations():
    try:
        locations = frappe.db.sql(
            """Select name,location_name from tabLocation;""", as_dict=True)
        return {"status": "success", "data": locations}
    except:
        return {"status": "failed"}


@frappe.whitelist(allow_guest=True)
def activate_user():
    try:
        user_details = json.loads(frappe.request.data)
        user = frappe.db.sql("""SELECT * from `tabUser` where email =%s or username=%s""",
                             (user_details["email"], user_details["email"]), as_dict=True)
        if not user:
            return {"status": "failed", "error": 'User Not Found'}
        else:
            customer = frappe.db.sql("""Select name from tabCustomer where customer =%s and activation_code =%s""", (
                user[0]["email"], user_details["activation_code"]), as_dict=True)

            if not customer:
                return {"status": "failed", "error": 'otp error'}
            else:
                cust_details = frappe.get_doc('Customer', customer[0].name)
                cust_details.customer_status = 1
                cust_details.save(ignore_permissions=True)

                user = frappe.get_doc('User', cust_details.customer)
                new_password = generate_otp(5)
                user.new_password = new_password

                if user.mobile_no:
                    send_sms(user.mobile_no,
                             f'Username: {user.username}, Password:{new_password}')
                frappe.db.commit()

            return {"status": "success", "data": cust_details}

    except BaseException as error:
        return {"status": "failed", "error": error}


@frappe.whitelist(allow_guest=True)
def register_user():
    try:
        new_user = json.loads(frappe.request.data)
        users = frappe.db.sql(
            """SELECT name from `tabUser` where email =%s or username=%s""", (new_user["email"], new_user["cpr"]), as_dict=True)

        if not users:
            # new user doc
            new_user_doc = frappe.get_doc({
                'doctype': 'User',
                'email': new_user["email"],
                'first_name': new_user["name"],
                'username': new_user["cpr"],
                'new_password': new_user["password"],
                'send_welcome_email': 0,
                'phone': new_user["mobile"],
                'mobile_no': new_user["mobile"]
            })
            new_user_doc.insert(ignore_permissions=True)

            otp = generate_otp(4)
            # new customer doc
            new_user_doc1 = frappe.get_doc({
                'doctype': 'Customer',
                'customer': new_user["email"],
                'customer_name': new_user["name"],
                'customer_name_arabic': new_user["name"],
                'flat_no': new_user["flat_no"],
                'block_no': new_user["block_no"],
                'bldg_no': new_user["bldg_no"],
                'road_no': new_user["road_no"],
                'area_name': new_user["area"],
                'city_name': new_user["city"],
                'customer_status': 0,
                'activation_code': otp,
                'location': new_user["location"],

            })
            new_user_doc1.insert(ignore_permissions=True)

            # set user roles and api authentication

            user_details = frappe.get_doc("User", new_user["email"])
            if not user_details.api_key:
                api_key = frappe.generate_hash(length=15)
                user_details.api_key = api_key

            api_secret = frappe.generate_hash(length=15)
            user_details.api_secret = api_secret
            user_details.flags.ignore_permissions = True
            # user_details.add_roles("Ecommerce")
            user_details.user_type = 'Website User'

            token = user_details.api_key + ":" + user_details.api_secret
            token_bytes = token.encode('ascii')
            base64_token = base64.b64encode(token_bytes)
            base64_message = base64_token.decode('ascii')
            user_data = {
                "userid": user_details.username,
                "username": user_details.first_name,
                "email": user_details.email,
                "token": base64_message,
                "mobile": user_details.mobile_no
            }
            user_details.save(ignore_permissions=True)

            if user_details.mobile_no:
                send_sms(user_details.mobile_no, f'Activation code: {otp}')

            frappe.db.commit()

            return {"status": "success", "data": user_data}
        else:
            return {"status": "failed", "data": 'User Exist'}
    except BaseException as error:
        frappe.db.rollback()
        return {"status": "failed", "error": error}


@frappe.whitelist(allow_guest=True)
def send_sms(_smsTo, content):
    try:
        smsTo = []
        smsTo.append(_smsTo)
        tokenURL = 'https://restapi.bulksmsonline.com/rest/api/v1/sms/gettoken/username/HameAl351/password/winsoft123'
        response = requests.get(tokenURL)
        json_resp = response.json()

        sendURL = 'https://restapi.bulksmsonline.com/rest/api/v1/sms/send'
        body = {'name': 'Maryja'}
        headers = {'content-type': 'application/json',
                   'token': json_resp["token"]}

        newSMS = {'from': 'SATER', 'to': smsTo,
                  'content': content, 'type': 'Unicode'}

        resp = requests.post(sendURL, data=json.dumps(newSMS), headers=headers)
        sms_gw_resp = resp.json()

        return {"status": "success", "data": sms_gw_resp}
    except BaseException as error:
        return {"status": "failed", "error": error}


@frappe.whitelist(allow_guest=True)
def generate_otp(digits=4):
    chars = string.digits
    random = ''.join(choice(chars) for _ in range(digits))
    return random


@frappe.whitelist(allow_guest=True)
def login():
    try:
        user_details = json.loads(frappe.request.data)
        if user_details:
            users = frappe.db.sql(
                """SELECT email from `tabUser` where enabled =1 and username=%s""", user_details["username"], as_dict=True)
            user = frappe.auth.check_password(
                users[0]["email"], user_details["password"])
            if user:
                user_details = frappe.get_doc("User", user)
                api_secret = frappe.generate_hash(length=15)
                if not user_details.api_key:
                    api_key = frappe.generate_hash(length=15)
                    user_details.api_key = api_key
                user_details.api_secret = api_secret
                user_details.save(ignore_permissions=True)

                token = user_details.api_key + ":" + api_secret
                token_bytes = token.encode('ascii')
                base64_token = base64.b64encode(token_bytes)
                base64_message = base64_token.decode('ascii')
                user_data = {
                    "username": user_details.username,
                    "first_name": user_details.first_name,
                    "email": user_details.email,
                    "token": base64_message,
                    "mobile": user_details.mobile_no,
                }

                return {"status": "success", "data": user_data}
        else:
            return {"status": "failed"}
        return user_details
    except:
        return {"status": "failed"}
