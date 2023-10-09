
import frappe
import json
import base64
import requests
import string
from random import choice
from frappe.utils.background_jobs import enqueue
import smtplib
import ssl
from email.mime.text import MIMEText




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
                                 f'Login password: {new_password}')
                    if user[0]["email"]:
                        send_email(user[0]["email"], f'AlSater Market Login Password',
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
                    if user[0]["email"]:
                        send_email(user[0]["email"], f'AlSater Market Login Password',
                                   f'Your login password: {new_password}')

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

                # user = frappe.get_doc('User', cust_details.customer)
                # new_password = generate_otp(5)
                # user.new_password = new_password

                # if user.mobile_no:
                #     send_sms(
                #         user.mobile_no, f'Username: {user.username}, Password:{new_password}')
                # if user.email:
                #     send_email(user.email, f'AlSater Market Login Password',
                #                f'Username: {user.username}, Password:{new_password}')
                frappe.db.commit()

            return {"status": "success", "data": cust_details}

    except BaseException as error:
        return {"status": "failed", "error": error}


#  temporrary api to sysnc loyal customers
@frappe.whitelist(allow_guest=True)
def sync_winsoftdb():
    try:
        users = frappe.db.sql("""Select C.customer as email,U.username as cpr,U.full_name as customer_name,C.location as locn,C.mobile_no ,'123456' as new_password,ifnull(C.flat_no,'') as flat_no,C.road_no,C.bldg_no,C.block_no,C.area_name,ifnull(C.city_name,'') as city_name from tabCustomer C inner join tabUser U on C.customer = U.name where U.username in ('920402836')	""", as_dict=True)
        response_list = []
        for user in users:
            newUserData = {
                'email': user["email"],
                'cpr': user["cpr"],
                'customer_name': user["customer_name"],
                'locn': user["locn"],
                'mobile_no': user["mobile_no"],
                'new_password': user["new_password"],
                'flat_no': user["flat_no"],
                'road_no': user["email"],
                'bldg_no': user["bldg_no"],
                'block_no': user["block_no"],
                'area_name': user["area_name"],
                'city_name': user["city_name"]
            }
            url = 'https://server.alsatermarket.com:4058/api/v1/Customer'
            response = requests.post(url, json=newUserData)
            response_list.append(response)

        if users:
            return {"status": "success", "data": response_list}
    except BaseException as error:
        return {"status": "failed", "data": error}


@frappe.whitelist(allow_guest=True)
def register_in_winsoft(new_user):
    try:
        # new_user = json.loads(frappe.request.data)
        newUserData = {
            'email': new_user["email"],
            'cpr': new_user["cpr"],
            'customer_name': new_user["name"],
            'locn': new_user["location"],
            'mobile_no': new_user["mobile"],
            'new_password': new_user["password"],
            'flat_no': new_user["flat_no"],
            'road_no': new_user["email"],
            'bldg_no': new_user["bldg_no"],
            'block_no': new_user["block_no"],
            'area_name': new_user["area"],
            'city_name': new_user["city"]
        }

        url = 'https://server.alsatermarket.com:4058/api/v1/Customer'
        response = requests.post(url, json=newUserData)
        return {"status": "success", "data": response}

    except BaseException as error:
        return {"status": "failed", "data": error}


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

            if user_details.email:
                send_email(user_details.email, f'AlSater Market',
                           f'Activation code: {otp}')

            frappe.db.commit()

            # Register in Winsoft
            register_in_winsoft(new_user)

            return {"status": "success", "data": user_data}
        else:
            return {"status": "failed", "data": 'User Exist'}
    except BaseException as error:
        frappe.db.rollback()
        return {"status": "failed", "error": error}


# @frappe.whitelist(allow_guest=True)
# def send_sms(_smsTo, content):
#     try:
#         smsTo = []
#         smsTo.append(_smsTo)
#         tokenURL = 'https://api.bulksmsonline.co/rest/api/v1/sms/gettoken/username/HameAl351/password/winsoft123'
#         response = requests.get(tokenURL)
#         json_resp = response.json()

#         sendURL = 'https://api.bulksmsonline.co/rest/api/v1/sms/send'
#         headers = {'content-type': 'application/json',
#                    'token': json_resp["token"]}

#         newSMS = {'from': 'SATER', 'to': smsTo,
#                   'content': content, 'type': 'Unicode'}

#         resp = requests.post(sendURL, data=json.dumps(newSMS), headers=headers)
#         sms_gw_resp = resp.json()

#         return {"status": "success", "data": sms_gw_resp}
#     except BaseException as error:
#         return {"status": "failed", "error": error}

# @frappe.whitelist(allow_guest=True)
# def send_sms(_smsTo, content):
#     try:

#         data_val = {
#             "Text": content,
#             "Number": _smsTo,
#             "SenderId": "ALSATER",
#             "Tool": "API"
#         }

#         headers = {
#             'Content-Type': 'application/json',
#             'Authorization': 'Basic ZUZRSjVmemdzdUxRb1JvanVYeG06eWh0aUtyZUI0TTZLNk16c3ZXd1dCNGFEa1V0a0ozeWRQT3NUTnhPUw=='
#         }
#         tokenURL = 'https://restapi.smscountry.com/v0.1/Accounts/eFQJ5fzgsuLQoRojuXxm/SMSes'
#         response = requests.post(
#             tokenURL, data=json.dumps(data_val), headers=headers)
#         json_resp = response.json()

#         return {"status": "success", "data": json_resp}
#     except BaseException as error:
#         return {"status": "failed", "error": error}

@frappe.whitelist(allow_guest=True)
def send_sms(_smsTo, content):
    try:

        tokenURL = 'http://api.smscountry.com/SMSCwebservice_bulk.aspx?User=Hamee31526&passwd=WinServer@301%&mobilenumber=' + \
            _smsTo+'&message='+content+'&sid=ALSATER&mtype=N&DR=Y'
        response = requests.get(tokenURL)
        # json_resp = response

        return {"status": "success", "data": response}
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


# @frappe.whitelist(allow_guest=True)
# def send_email(_emailTo, email_subject, content):
#     try:
#         email_args = {
#             "recipients": [_emailTo],
#             "message": content,
#             "subject": email_subject
#         }
#         enqueue(method=frappe.sendmail, queue='short',
#                 timeout=300, event="sendmail", **email_args)

#         return {"status": "success", "data": "Successfully Send Email"}
#     except BaseException as error:
#         return {"status": "failed", "error": error}

@frappe.whitelist(allow_guest=True)
def send_email(_emailTo, email_subject, message):
    try:
        smtp_server = "smtp.gmail.com"
        port = 587  # For starttls
        sender_email = "ecommerce.alsater@gmail.com"
        password = "knpddyvzpqtkosdo"

        msg = MIMEText(message, 'html')
        msg['Subject'] = 'AlSater Login Details'
        msg['From'] = "Al Sater Market"
        msg['To'] = _emailTo

        context = ssl.create_default_context()

        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, _emailTo, msg.as_string())
        server.close()

        return {"status": "success", "data": "Successfully Send Email"}
    except BaseException as error:
        return {"status": "failed", "error": error}
