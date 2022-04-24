import frappe
import json


@frappe.whitelist()
def get_all_invoices(customer_email):
    try:
        invoices = frappe.db.sql(
            """Select I.name,I.customer,invoice_number,invoice_date,amount,discount_amount,vat,total_amount  from tabUser U inner join tabCustomer C on U.name = C.customer inner join tabInvoice I on I.customer = U.username where C.customer =%s""", customer_email, as_dict=True)
        if invoices:
            for invoice in invoices:
                invoice["items"] = frappe.db.sql(
                    """Select parent,idx,item_name,qty,unit,unit_price,vat,price,vat_type from tabInvoiceDetails where parent=%s""", invoice.name, as_dict=True)

            return {"status": "success", "data": invoices}
        else:
            return {"status": "failed"}
    except:
        return {"status": "failed"}
