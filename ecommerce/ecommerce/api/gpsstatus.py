import frappe
import json

@frappe.whitelist(allow_guest=True)
def save():
    try:
        gps_details = json.loads(frappe.request.data)
        user_gps_status = frappe.db.sql("""Select * from `tabGPS Status` where user = %s  """,gps_details["user_email"], as_dict=True)
        if not user_gps_status:
            doc = frappe.get_doc({
                'doctype': 'GPS Status',
                'user': gps_details["user_email"],
                'latitude': gps_details["latitude"],
                'longitude': gps_details["longitude"]
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()        
        else:
            doc = frappe.get_doc('GPS Status', user_gps_status[0]["name"])
            doc.latitude = gps_details["latitude"]
            doc.longitude = gps_details["longitude"]
            doc.save(ignore_permissions=True)
            frappe.db.commit()
        
        return {"status": "success", "data": {"user_email": doc.user, "latitude": doc.latitude , "longitude": doc.longitude }}
        
    except BaseException as error:
        return {"status": "failed", "error": error}
    

@frappe.whitelist(allow_guest=True)
def getgpsdata(emailID):
    try:
        user_gps_status = frappe.db.sql("""Select * from `tabGPS Status` where user = %s """,emailID, as_dict=True)
        if user_gps_status:
            return {"status": "success", "data": {"user_email": user_gps_status[0]["user"], "latitude":  user_gps_status[0]["latitude"] , "longitude": user_gps_status[0]["longitude"]  }}
        else:
            return {"status": "failed", "error": 'User Not Found'}     

    except BaseException as error:
        return {"status": "failed", "error": error}


@frappe.whitelist(allow_guest=True)
def getShopLocation(email):
    try:
        staff_data = frappe.db.sql("""select E.name as emp_id, E.staff_name,E.mobile_no,E.employee as email, L.name as loc_id , L.location_name,L.latitude, L.longitude  from tabEmployees E inner join tabLocation L on E.location = L.name where E.employee = %s """,email, as_dict=True)
        if staff_data:
            shopLocation= { "emp_id": staff_data[0]["emp_id"],
                            "staff_name": staff_data[0]["staff_name"], 
                            "mobile_no": staff_data[0]["mobile_no"], 
                            "email": staff_data[0]["email"], 
                            "loc_id": staff_data[0]["loc_id"], 
                            "location_name": staff_data[0]["location_name"], 
                            "latitude": staff_data[0]["latitude"], 
                            "longitude": staff_data[0]["longitude"] } 
            return {"status": "success", "data": shopLocation}
        else:
            return {"status": "failed", "error": error}

    except BaseException as error:
        return {"status": "failed", "error": error}