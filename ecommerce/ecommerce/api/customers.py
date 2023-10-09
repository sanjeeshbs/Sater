import frappe
import json


@frappe.whitelist()
def get_customer(customer):
    try:
        customer = frappe.db.sql(
            """call get_customer(%s);""", customer, as_dict=True)
        if customer:
            customer[0]["shipping"] = frappe.db.sql(
                """Select name,flat_number,building_number,road_number,block_number,area_name, city_name, primary_address from `tabShipping Address` where customer =%s""", customer[0].name, as_dict=True)
            return {"status": "success", "data": customer[0]}
        else:
            return {"status": "failed"}
    except:
        return {"status": "failed"}


@frappe.whitelist()
def update_profile():
    try:
        customer_details = json.loads(frappe.request.data)
        customer = frappe.get_doc('Customer', customer_details["name"])

        customer.customer_name = customer_details["first_name"]
        customer.mobile_no = customer_details["mobile_no"]
        customer.flat_no = customer_details["flat_no"]
        customer.bldg_no = customer_details["bldg_no"]
        customer.road_no = customer_details["road_no"]
        customer.block_no = customer_details["block_no"]
        customer.area_name = customer_details["area_name"]
        customer.city_name = customer_details["city_name"]
        customer.location = customer_details["location"]

        customer.save()
        frappe.db.commit()

        return {"status": "success", "data": customer}
    except:
        return {"status": "failed"}


@frappe.whitelist()
def delete_shipping_address(name):
    try:
        data = frappe.db.sql(
            """Delete from `tabShipping Address` where name =%s""", name, as_dict=True)
        frappe.db.commit()
        return {"status": "success", "data": data}
    except:
        return {"status": "failed"}


@frappe.whitelist()
def save_shipping_address():
    try:
        sh = json.loads(frappe.request.data)

        if sh["primary_address"]:
            frappe.db.sql(
                """update `tabShipping Address` set primary_address=0""")

        if not sh["name"]:
            data = frappe.db.sql(
                """Select name from tabCustomer where customer =%s""", sh["customer_email"], as_dict=True)

            doc = frappe.get_doc({
                'doctype': 'Shipping Address',
                'customer': data[0].name,
                'flat_number': sh["flat_number"],
                'building_number': sh["building_number"],
                'road_number': sh["road_number"],
                'block_number': sh["block_number"],
                'area_name': sh["area_name"],
                'city_name': sh["city_name"],
                'primary_address': sh["primary_address"]
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            customer = get_customer_details(sh["customer_email"])
            return {"status": "success", "data": customer}
        else:
            doc = frappe.get_doc('Shipping Address', sh["name"])

            doc.flat_number = sh["flat_number"]
            doc.building_number = sh["building_number"]
            doc.road_number = sh["road_number"]
            doc.block_number = sh["block_number"]
            doc.area_name = sh["area_name"]
            doc.city_name = sh["city_name"]
            doc.primary_address = sh["primary_address"]            
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            customer = get_customer_details(sh["customer_email"])
            return {"status": "success", "data": customer}

    except:
        return {"status": "failed"}


def get_customer_details(customer):
    customer = frappe.db.sql(
        """call get_customer(%s);""", customer, as_dict=True)
    if customer:
        customer[0]["shipping"] = frappe.db.sql(
            """Select name,flat_number,building_number,road_number,block_number,area_name, city_name, primary_address from `tabShipping Address` where customer =%s""", customer[0].name, as_dict=True)
        return customer[0]
    else:
        return None


# @frappe.whitelist()
# def save_shipping_address(name=''):
#     try:
#         sh = json.loads(frappe.request.data)
#         data = frappe.db.sql(
#             """Select name from tabCustomer where customer =%s""", sh["customer_email"], as_dict=True)
#         doc = frappe.get_doc('Customer', data[0].name)

#         if not name:
#             doc.append("shipping", {"flat_number": sh["flat_number"], "building_number": sh["building_number"],                   "road_number": sh["road_number"],
#                        "block_number": sh["block_number"], "area_name": sh["area_name"], "ciuty_name": sh["city_name"], "primary_address": sh["primary_address"]})
#         else:
#             filtered = [d for d in doc.shipping if d.name == name]
#             filtered[0].flat_number = sh["flat_number"]
#             filtered[0].building_number = sh["building_number"]
#             filtered[0].road_number = sh["road_number"]
#             filtered[0].block_number = sh["block_number"]
#             filtered[0].area_name = sh["area_name"]
#             filtered[0].ciuty_name = sh["city_name"]
#             filtered[0].primary_address = sh["primary_address"]

#         doc.save()
#         frappe.db.commit()

#         return {"status": "success", "data": doc}
#     except:
#         return {"status": "failed"}


# doc = frappe.new_doc("Parent")
# doc.append("childfield", { ... })
