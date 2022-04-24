import frappe
import json
import requests


@frappe.whitelist(allow_guest=True)
def gatee_callback(payment_id):
    try:
        if payment_id:

            merchant_id = frappe.db.get_value(
                'AppSettings', 'gatee_unique_id', 'settings_value')
            gatee_hash = frappe.db.get_value(
                'AppSettings', 'gatee_hash', 'settings_value')
            merchant_id = frappe.db.get_value(
                'AppSettings', 'gatee_unique_id', 'settings_value')
            gatee_get_payment_details_url = frappe.db.get_value(
                'AppSettings', 'gatee_get_payment_details_url', 'settings_value')

            if merchant_id and gatee_hash and merchant_id and gatee_get_payment_details_url:
                url = gatee_get_payment_details_url + '?unique_id='
                url += merchant_id + '&hash=' + gatee_hash + '&payment_id=' + payment_id
                response = requests.get(url)
                json_resp = response.json()

                doc = frappe.get_doc('Orders', json_resp["field2"])

                if doc:
                    doc.pay_id = json_resp["transactions"]["id"]
                    doc.pay_date = json_resp["transactions"]["date"]
                    doc.acq_trans_id = json_resp["transactions"]["acquirer_transaction_id"]
                    doc.authorization_code = json_resp["transactions"]["authorization_code"]
                    doc.pay_currency = json_resp["transactions"]["currency"]
                    doc.invoice_id = json_resp["transactions"]["invoice_id"]
                    doc.payed_amount = json_resp["transactions"]["paid_amount"]
                    doc.card_brand = json_resp["transactions"]["card_brand"]
                    doc.card_type = json_resp["transactions"]["card_type"]
                    doc.invoice_number = json_resp["invoices"]["invoice_number"]
                    doc.invoice_status = json_resp["invoices"]["invoice_status"]
                    doc.pay_customer_name = json_resp["invoices"]["customer_name"]
                    doc.pay_customer_email = json_resp["invoices"]["customer_email"]
                    if json_resp["invoices"]["customer_mobile"]:
                        doc.pay_customer_mobile = json_resp["invoices"]["customer_mobile"]

                    doc.save(ignore_permissions=True)
                    frappe.db.commit()

            return {"status": "success", "data": json_resp}

        else:
            return {"status": "failed"}

    except BaseException as error:
        return {"status": "failed", "data": error}
