
import frappe
import json

@frappe.whitelist(allow_guest=True)
def getstatus(order):
    try:
        order_data = frappe.db.sql("""Select * from  `tabOrder Status` where `order` =  %s """,order, as_dict=True)
        order_status =[]
        for order in order_data:
            order_status.append({"order": order["order"], "order_status": order["order_status"],"update_time": order["update_time"]})
        
        return {"status": "success", "data": order_status}
    except BaseException as error:
        return {"status": 'failed', "error": error}


@frappe.whitelist(allow_guest=True)
def getorderstatus(order):
    try:
        order_data = frappe.db.sql("""Select O.name,O.order_status, O.employee, O.employee_name, E.mobile_no, E.employee as email from `tabOrders` O left join tabEmployees E on O.employee = E.name  where O.name =   %s """,order, as_dict=True)
        if order_data:
            order_status = frappe.db.sql("""Select * from  `tabOrder Status` where `order` =  %s """,order, as_dict=True)
            if order_status:
                order_status_data =[]
                for order in order_status:
                    order_status_data.append({"order": order["order"], "order_status": order["order_status"],"update_time": order["update_time"]})
                order_data[0].update({"status" : order_status_data})
            
            return {"status": "success", "data": order_data[0]}
                
        else:
            return {"status": "failed", "data": "Not Found"}
        return {"status": "success", "data": order_data}
    except BaseException as error:
        return {"status": 'failed', "error": error}