import frappe
import json


@frappe.whitelist(allow_guest=True)
def get_timeslotes():
    try:
        timeslotes = frappe.db.sql(
            """call get_timeslotes('MOB');""", as_dict=True)
        if timeslotes:
            # message.status, message.data[]
            return {"status": "success", "data": timeslotes}
        else:
            return {"status": "failed"}
    except:
        return {"status": "failed"}
