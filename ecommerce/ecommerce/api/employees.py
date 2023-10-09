import frappe
import json


@frappe.whitelist(allow_guest=True)
def get_employees():
    try:
        return {"status": "success"}
        # customer = frappe.db.sql(
        #     """call get_customer(%s);""", customer, as_dict=True)
        # if customer:
        #     customer[0]["shipping"] = frappe.db.sql(
        #         """Select name,flat_number,building_number,road_number,block_number,area_name, city_name, primary_address from `tabShipping Address` where customer =%s""", customer[0].name, as_dict=True)
        #     return {"status": "success", "data": customer[0]}
        # else:
        #     return {"status": "failed"}
    except:
        return {"status": "failed"}