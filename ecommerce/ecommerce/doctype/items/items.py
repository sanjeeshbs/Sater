# Copyright (c) 2021, Sanjeesh and contributors
# For license information, please see license.txt

from hashlib import sha224
import frappe
import json
import requests
from frappe.model.document import Document

class Items(Document):
    pass

@frappe.whitelist()
def update_category(category, items):
    try:
        items_list = json.loads(items)
        # doc = frappe.get_doc('Items', items_list[0])
        for item in items_list:
            doc = frappe.get_doc('Items', item)
            doc.group_name = category
            # doc.image_name = ''
            doc.save()
        frappe.db.commit()
        return {"status": "success"}
    except BaseException as error:
        return {"status": "failed", "data": error}


@frappe.whitelist()
def update_item_master():
    try:
        url = 'https://server.alsatermarket.com:4058/api/v1/Products'
        response = requests.get(url)
        products = response.json()
        for product in products:
            item_status = False
            if product['item_status'] == 'Y':
                item_status = True
            else:
                item_status = False

            item = frappe.db.sql(
                """Select name from tabItems where item_code=%s;""", product['item_code'], as_dict=True)
            if item:
                doc1 = frappe.get_doc('Items', item[0]['name'])
                doc1.item_name = product['item_name']
                doc1.item_status = item_status
                doc1.on_hand = product['on_hand']
                # if product['image_name']:
                # doc1.image_name = product['image_name']
                # doc1.image_name = '\/files\/' + str(product['image_name'])
                for barcode in product['barcodes']:
                    filtered = [
                        b for b in doc1.barcodes if b.barcode == barcode['barcode']]
                    if filtered:
                        filtered[0].unit_name = barcode['unit_name']
                        filtered[0].price = barcode['price']
                        filtered[0].factor_value = barcode['factor_value']
                        filtered[0].vat_code = barcode['vat_code']
                        filtered[0].vat_value = barcode['vat_value']
                        filtered[0].desc_english = barcode['desc_english']
                        filtered[0].unit_name = barcode['unit_name']
                        filtered[0].desc_arabic = barcode['desc_arabic']
                    else:
                        doc1.append('barcodes', {
                            'barcode': barcode['barcode'],
                            'unit_name': barcode['unit_name'],
                            'price': barcode['price'],
                            'factor_value': barcode['factor_value'],
                            'vat_code': barcode['vat_code'],
                            'vat_value': barcode['vat_value'],
                            'desc_english': barcode['desc_english'],
                            'desc_arabic': barcode['desc_arabic']
                        })

                doc1.save()
            else:
                image_name = ''
                if product['image_name']:
                    image_name = '/files/' + str(product['image_name'])
                    # image_name = str(product['image_name'])
                doc2 = frappe.get_doc(
                    {'doctype': 'Items',
                     'item_code': product['item_code'],
                     'item_name': product['item_name'],
                     'item_status': item_status,
                     'on_hand': product['on_hand'],
                     'group_name' : '000008',
                     'image_name' :  image_name
                     })
                for barcode in product['barcodes']:
                    doc2.append('barcodes', {
                        'barcode': barcode['barcode'],
                        'unit_name': barcode['unit_name'],
                        'price': barcode['price'],
                        'factor_value': barcode['factor_value'],
                        'vat_code': barcode['vat_code'],
                        'vat_value': barcode['vat_value'],
                        'desc_english': barcode['desc_english'],
                        'desc_arabic': barcode['desc_arabic']
                    })
                doc2.insert()

        frappe.db.commit()
        return {"status": "success"}

    except BaseException as error:
        return {"status": "failed", "data": error}
