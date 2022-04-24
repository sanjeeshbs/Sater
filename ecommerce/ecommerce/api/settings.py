import frappe
import json


@frappe.whitelist(allow_guest=True)
def get_settings():
    try:
        settings = frappe.db.sql(
            """Select settings_name, settings_value from  tabAppSettings""", as_dict=True)
        if settings:
            # message.status, message.data[]
            return {"status": "success", "data": settings}
        else:
            return {"status": "failed"}
    except:
        return {"status": "failed"}
