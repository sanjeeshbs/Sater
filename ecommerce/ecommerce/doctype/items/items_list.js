frappe.listview_settings['Items'] = {
    // colwidths: { "item_name": 2 },
    // add_fields: ["item_code", "item_name", "item_status"],
    // filters: [["item_status", "=", "1"]],

    onload(listview) {
        listview.page.add_menu_item(__("Update Products"), function () {
            frappe.call({
                method: 'ecommerce.ecommerce.doctype.items.items.update_item_master',
                callback: function (r) {
                    if (r.message.status == 'success') {
                        listview.refresh();
                        frappe.msgprint('Products updated successfully.');
                    } else {
                        frappe.msgprint('Failed to update.');
                    }

                }
            });
        });

        listview.page.add_action_item(__("Set Product Category"), function () {
            let d = new frappe.ui.Dialog({
                title: 'Enter details',
                fields: [
                    {
                        fieldname: "group_name",
                        fieldtype: "Link",
                        label: "Group Name",
                        options: "Groups"
                    },
                ],
                primary_action_label: 'Submit',
                primary_action(values) {
                    // console.log(values.group_name);
                    const selected_docs = listview.get_checked_items();
                    let selected_product_ids = selected_docs.map(function (val, index) {
                        return val.name;
                    });
                    console.log('selected_docs:', selected_product_ids);
                    frappe.call({
                        method: 'ecommerce.ecommerce.doctype.items.items.update_category',
                        args: {
                            items: selected_product_ids,
                            category: values.group_name
                        },
                        callback: function (r) {
                            console.log('r', r);
                            if (r.message.status == 'success') {
                                console.log('Data1:', r.message.data1);
                                console.log('Data2:', r.message.data2);
                                listview.refresh();
                                frappe.msgprint('Products updated successfully.');
                            } else {
                                frappe.msgprint('Failed to update.');
                            }

                        }
                    });
                    d.hide();
                }
            });

            d.show();
        });
    },

    // get_indicator: function(doc) {
    // 	var indicator = [__(doc.item_status), frappe.utils.guess_colour(doc.item_status), "status,=," + doc.item_status];
    // 	indicator[1] = {"Active": "green", "Inactive": "red", "Left": "gray", "Suspended": "orange"}[doc.status];
    // 	return indicator;
    // }
};
