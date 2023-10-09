import frappe
import json

g_groups = []


@frappe.whitelist(allow_guest=True)
def get_all_groups():
    try:
        groups = frappe.db.sql(
            """SELECT name,group_name,image_name,group_name_arabic FROM tabGroups where parent_group_name='000008'""", as_dict=True)
        if groups:
            # message.status, message.data[]
            return {"status": "success", "data": groups}
        else:
            return {"status": "failed"}
    except:
        return {"status": "failed"}


@frappe.whitelist(allow_guest=True)
def get_group_with_name(name):
    try:
        group = frappe.db.sql(
            """SELECT name,group_name,image_name,group_name_arabic FROM tabGroups where name=%s""", name, as_dict=True)
        if group:
            # message.status, message.data[]
            return {"status": "success", "data": group}
        else:
            return {"status": "failed"}
    except:
        return {"status": "failed"}


@frappe.whitelist(allow_guest=True)
def get_sub_group_of(group):
    try:
        groups = frappe.db.sql(
            """SELECT name,group_name,image_name,group_name_arabic FROM tabGroups where parent_group_name=%s""", group, as_dict=True)
        if groups:
            # message.status, message.data[]
            return {"status": "success", "data": groups}
        else:
            return {"status": "failed"}
    except:
        return {"status": "failed"}


# @frappe.whitelist()
# def get_child_groups_of(group):
#     try:
#         global g_groups
#         g_groups = []
#         fill_groups(group)
#         if g_groups:
#             return {"status": "success", "data": g_groups}
#         else:
#             return {"status": "failed"}
#     except:
#         return {"status": "failed"}


# def fill_groups(group):
#     global g_groups
#     l_groups = frappe.db.sql(
#         """SELECT name,group_name,image_name,group_name_arabic FROM tabGroups where parent_group_name=%s""", group, as_dict=True)
#     for group in l_groups:
#         g_groups.append(group)
#         fill_groups(group.name)
