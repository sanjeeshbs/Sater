# Copyright (c) 2021, Sanjeesh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import utils


class Orders(Document):
    def before_save(self):
        try:
            order_status = frappe.db.sql("""Select * from  `tabOrder Status` where `order` = %s  and `order_status` = %s """,(self.name, self.order_status), as_dict=True)
            if not order_status:
                doc = frappe.get_doc({
                'doctype': 'Order Status',
                'order': self.name,
                'order_status': self.order_status,
                'update_time': utils.now()
                })
                doc.insert(ignore_permissions=True)
                frappe.db.commit() 
            else:
                doc = frappe.get_doc('Order Status', order_status[0]["name"])
                doc.order_status = self.order_status
                doc.update_time = utils.now()
                doc.save(ignore_permissions=True)
                frappe.db.commit()
        except BaseException as error:
            return {"status": "failed", "error": error}        


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_item_units(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""Select unit_name from tabBarcodes where parent =%s""", filters.get('item'))


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_time_slotes(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""call get_timeslotes('WEB');""")


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_shipping_address(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""Select name,concat( 'Flat: ',flat_number, ', Bldg: ',building_number,', Road: ', road_number,', Block: ',block_number,', Area: ',area_name,', City: ' ,city_name) as address from `tabShipping Address` where customer =%s""", filters.get('customer'))


@frappe.whitelist()
def get_item_details(item, unit=None):
    if unit:
        return frappe.db.sql("""Select parent,barcode,unit_name,price,factor_value,vat_code,vat_value,desc_english,desc_arabic from tabBarcodes where parent =%s and unit_name=%s""", (item, unit), as_dict=True)
    else:
        return frappe.db.sql("""Select name,item_code,item_name,group_name,item_status,on_hand from tabItems where name =%s""", item, as_dict=True)
