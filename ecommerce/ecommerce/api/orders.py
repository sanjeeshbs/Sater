from xml.dom.minidom import parseString
import frappe
import json
from frappe import utils


# @frappe.whitelist()
# def get_order_with_id(name):
#     try:
#         if name:
#             order = frappe.db.sql("""Select name,customer,shipping_address,payment_method,order_date,time_slote,order_status,amount,total_amount,customer_name,shipping_address_details,payment_status, customer_remarks, order_status from `tabOrders` where name =%s""", name, as_dict=True)
#             if order:
#                 order[0]["items"] = frappe.db.sql(
#                     """Select name,parent,idx,item,item_name,unit_name,barcode,qty,unit_price,vat,total_price,factor from tabOrderDetails where parent =%s""", order[0]["name"], as_dict=True)
#             return {"status": "success", "data": order[0]}
#     except BaseException as error:
#         return {"status": 'failed', "error": error}

@frappe.whitelist()
def get_order_with_id(name):
    try:
        if name:
            order = frappe.db.sql("""Select name as id,name as order_no, customer as customer_id,order_date,total_amount as amount,payment_method,shipping_address as shipping_address_id,time_slote as time_slote_id, customer_remarks,customer_remarks as remarks,order_status as status from `tabOrders` where name =%s""", name, as_dict=True)
            if order:
                order[0]["orderDetails"] = frappe.db.sql(
                    """Select name as id, parent as order_no, item as product_id,item as item_code,barcode,unit_name as uom, factor, qty,unit_price,vat from `tabOrderDetails` where parent =%s""", order[0]["id"], as_dict=True)
                for orderDetail in order[0]["orderDetails"]:
                    orderDetail["product"] = frappe.db.sql(
                        """Select name,item_code,item_name,group_name,item_status,on_hand,image_name from tabItems where name =%s""", orderDetail["product_id"], as_dict=True)[0]
                    orderDetail["product"]["barcodes"] = frappe.db.sql(
                        """select parent,barcode,unit_name,price,factor_value,vat_code,vat_value,desc_english,desc_arabic from tabBarcodes where parent =%s""", orderDetail["product_id"], as_dict=True)

            return {"status": "success", "data": order[0]}
    except BaseException as error:
        return {"status": 'failed', "error": error}


@frappe.whitelist()
def get_order(customer_email):
    try:
        if customer_email:
            data = frappe.db.sql(
                """Select name from tabCustomer where customer =%s""", customer_email, as_dict=True)
            if data:
                order_list = frappe.db.sql(
                    """Select name,customer,shipping_address,payment_method,order_date,time_slote,order_status,amount,total_amount,customer_name,shipping_address_details,payment_status from `tabOrders` where customer =%s""", data[0].name, as_dict=True)
                for order in order_list:
                    order["items"] = frappe.db.sql(
                        """Select name,parent,idx,item,item_name,unit_name,barcode,qty,unit_price,vat,total_price,factor from tabOrderDetails where parent =%s""", order["name"], as_dict=True)
                return {"status": "success", "data": order_list}
            else:
                return {"status": "failed", "data": []}
        else:
            return {"status": 'failed', "error": 'Bad Request'}
    except BaseException as error:
        return {"status": 'failed', "error": error}


@frappe.whitelist()
def get_all_orders():
    try:
        order_list = frappe.db.sql("""Select name,customer,shipping_address,payment_method,order_date,time_slote,order_status,amount,total_amount,customer_name, shipping_address_details,payment_status from `tabOrders` order by order_date desc""", as_dict=True)
        if order_list:
            for order in order_list:
                order["items"] = frappe.db.sql(
                        """Select name,parent,idx,item,item_name,unit_name,barcode,qty,unit_price,vat,total_price,factor,product_image_name from tabOrderDetails where parent =%s""", order["name"], as_dict=True)
            return {"status": "success", "data": order_list}
        else:
                return {"status": "failed", "data": []}

    except BaseException as error:
        return {"status": 'failed', "error": error}

@frappe.whitelist()
def get_assaigned_orders(staffEmail):
    try:
        userDetalis = frappe.db.sql(
            """Select * from tabEmployees where employee =%s""", staffEmail, as_dict=True)
        order_list = frappe.db.sql("""Select name,customer,shipping_address,payment_method,order_date,time_slote,order_status,amount,total_amount,customer_name, shipping_address_details,payment_status from `tabOrders` where employee = %s order by order_date desc""", userDetalis[0].name, as_dict=True)
        if order_list:
            for order in order_list:
                order["items"] = frappe.db.sql(
                        """Select name,parent,idx,item,item_name,unit_name,barcode,qty,unit_price,vat,total_price,factor,product_image_name from tabOrderDetails where parent =%s""", order["name"], as_dict=True)
            return {"status": "success", "data": order_list}
        else:
                return {"status": "failed", "data": []}

    except BaseException as error:
        return {"status": 'failed', "error": error}


@frappe.whitelist()
def update_order_status():
    try:
        orderDetails = json.loads(frappe.request.data)
        order = frappe.get_doc('Orders', orderDetails["name"])
        if order:
            order.order_status = orderDetails["order_status"]
            order.save(ignore_permissions=True)
            frappe.db.commit()
            return {"status": "success", "data": [order]}
        else:
            return {"status": "failed"}
        
    except BaseException as error:
        return {"status": 'failed', "error": error}

# @frappe.whitelist()
# def get_item_image(item):
#     try:
#         data = frappe.db.sql(
#             """Select image_name from tabItems where item_code  =%s""", item, as_dict=True)
#         return data[0].image_name
#     except BaseException as error:
#         print(f'\n\n\n\n\nError: {error}\n\n\n\n\n')
#         return ""


@frappe.whitelist()
def save_order():
    try:
        order = json.loads(frappe.request.data)
        data = frappe.db.sql(
            """Select name from tabCustomer where customer =%s""", order["customer_id"], as_dict=True)

        doc = frappe.get_doc({
            'doctype': 'Orders',
            'customer': data[0].name,
            'shipping_address': order["shipping_address_id"],
            # 'order_date': frappe.utils.get_datetime(order["order_date"]).strftime('%Y-%m-%d'),
            # 'order_time': frappe.utils.get_datetime(order["order_date"]).strftime('%H:%M:%S'),
            'order_date': frappe.utils.get_datetime(utils.now()).strftime('%Y-%m-%d'),
            'order_time': frappe.utils.get_datetime(utils.now()).strftime('%H:%M:%S'),
            'time_slote': order["time_slote_id"],
            'payment_method': order["payment_method"],
            'payment_status': "Not Payed",
            'amount': order["amount"],
            'vat': order["amount"],
            'total_amount': order["amount"],
            'customer_remarks': order["customer_remarks"]
        })
        total_vat = 0
        for item in order["orderDetails"]:
            data = frappe.db.sql(
                """Select image_name from tabItems where name  =%s""", item["product_id"], as_dict=True)
            image_name = data[0].image_name
            # image_name = item["product_id"]
            vat = (item["qty"] * item["unit_price"]) * \
                (float(item["vat"]) / 100.0)
            total_price = item["qty"] * item["unit_price"]
            doc.append('items', {"item": item["product_id"], "unit_name": item["uom"], "qty": item["qty"],
                       "unit_price": item["unit_price"], "vat": vat, "total_price": total_price, "barcode": item["barcode"], "product_image_name": image_name})
            total_vat += vat
        doc.vat = total_vat
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "success", "data": doc}
    except BaseException as error:
        print(f'\n\n\n\n\nError: {error}\n\n\n\n\n')
        return {"status": 'failed', "error": error}
