
import frappe
import json


@frappe.whitelist(allow_guest=True)
def get_all_banners():
    try:
        banners = frappe.db.sql(
            """Select name,banner_name,image_name from  `tabBanners`""", as_dict=True)
        if banners:
            # message.status, message.data[]
            return {"status": "success", "data": banners}
        else:
            return {"status": "failed"}
    except:
        return {"status": "failed"}


@frappe.whitelist(allow_guest=True)
def get_all_flyers():
    try:
        flyers = frappe.db.sql(
            """SELECT name,flyer_name,image_name,flyer_status from tabFlyers where flyer_status =1 order by flyer_name""", as_dict=True)
        if flyers:
            # message.status, message.data[]
            return {"status": "success", "data": flyers}
        else:
            return {"status": "failed"}
    except:
        return {"status": "failed"}
