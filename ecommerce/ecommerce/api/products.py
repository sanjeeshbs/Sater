
import frappe
import json


class Product:
    def __init__(self):
        self.groups = []
        self.products = []

    def get_products_of_group(self, group_name):
        self.groups = []
        self.products = []
        self.fill_groups_and_products(group_name)
        if not self.products:
            l_products = frappe.db.sql(
                """Select name,item_code,item_name,group_name,item_status,on_hand,image_name from tabItems where item_status = 1 and group_name =%s""", group_name, as_dict=True)
            return l_products
        return self.products

    # recurssive function to loop through  a tree node
    def fill_groups_and_products(self, group_name):
        l_groups = frappe.db.sql(
            """SELECT name,group_name,image_name,group_name_arabic FROM tabGroups where parent_group_name=%s""", group_name, as_dict=True)
        for l_group in l_groups:
            l_products = frappe.db.sql(
                """Select name,item_code,item_name,group_name,item_status,on_hand,image_name from tabItems where item_status = 1 and group_name =%s""", l_group.name, as_dict=True)
            for l_product in l_products:
                self.products.append(l_product)
            self.groups.append(l_group)
            self.fill_groups_and_products(l_group.name)

################################################################################################################


@frappe.whitelist()
def get_product(product_name):
    try:
        products = frappe.db.sql(
            """Select name,item_code,item_name,group_name,item_status,on_hand,image_name from tabItems where item_status = 1 and name =%s""", product_name, as_dict=True)
        if products:
            for product in products:
                product["barcodes"] = frappe.db.sql(
                    """Select parent,barcode,unit_name,price,factor_value,vat_code,vat_value,desc_english,desc_arabic from tabBarcodes where parent =%s""", product["name"], as_dict=True)
            return {"status": "success", "data": products[0]}  # message.status, message.data[]
        else:
            return {"status": "failed"}
    except:
        return {"status": "failed"}


@frappe.whitelist()
def get_product_by_barcode(barcode):
    try:
        products = frappe.db.sql(
            """Select I.name,item_code,item_name,group_name,item_status,on_hand,image_name from tabItems I inner join tabBarcodes B on I.name = B.parent where I.item_status = 1 and B.barcode =%s""", barcode, as_dict=True)
        if products:
            for product in products:
                product["barcodes"] = frappe.db.sql(
                    """Select parent,barcode,unit_name,price,factor_value,vat_code,vat_value,desc_english,desc_arabic from tabBarcodes where parent =%s""", product["name"], as_dict=True)
            return {"status": "success", "data": products[0]}  # message.status, message.data[]
        else:
            return {"status": "failed"}
    except:
        return {"status": "failed"}


@frappe.whitelist()
def get_products_like(name):
    try:
        products = frappe.db.sql(
            """Select name,item_code,item_name,group_name,item_status,on_hand,image_name from tabItems where item_status = 1 and item_name like %s""", "%{0}%".format(name), as_dict=True)
        if products:
            for product in products:
                product["barcodes"] = frappe.db.sql(
                    """Select parent,barcode,unit_name,price,factor_value,vat_code,vat_value,desc_english,desc_arabic from tabBarcodes where parent =%s""", product["name"], as_dict=True)
            return {"status": "success", "data": products}  # message.status, message.data[]
        else:
            return {"status": "failed"}
    except:
        return {"status": "failed"}


@frappe.whitelist()
def get_all_products(group_name):
    try:
        if not group_name:
            products = frappe.db.sql(
                """Select name,item_code,item_name,group_name,item_status,on_hand,image_name from tabItems where item_status = 1 limit 100 """, as_dict=True)
            if products:
                for product in products:
                    product["barcodes"] = frappe.db.sql(
                        """Select parent,barcode,unit_name,price,factor_value,vat_code,vat_value,desc_english,desc_arabic from tabBarcodes where parent =%s""", product["name"], as_dict=True)
                return {"status": "success", "data": products}  # message.status, message.data[]
            else:
                return {"status": "failed"}

        product = Product()
        products = product.get_products_of_group(group_name)
        if products:
            for product in products:
                product["barcodes"] = frappe.db.sql(
                    """Select parent,barcode,unit_name,price,factor_value,vat_code,vat_value,desc_english,desc_arabic from tabBarcodes where parent =%s""", product["name"], as_dict=True)
            return {"status": "success", "data": products}  # message.status, message.data[]
        else:
            return {"status": "failed"}

    except:
        return {"status": "failed"}
