frappe.listview_settings['Customer'] = {
    add_fields: ['customer_status'],
    hide_name_column: true,
    get_indicator(doc) {
        // customize indicator color
        if (doc.customer_status) {
            return [__("Active"), "green", "customer_status,=,1"];
        } else {
            return [__("Not Active"), "red", "customer_status,=,0"];
        }
    },
    onload(listview) {
        listview.page.add_menu_item(__("Update Customers"), function () {
            frappe.call({
                method: 'ecommerce.ecommerce.doctype.customer.customer.update_customer',
                callback: function (r) {
                    if (r.message.status == 'success') {
                        console.log(r.message.data);
                        listview.refresh();
                        frappe.msgprint('Customers updated successfully.');
                    } else {
                        frappe.msgprint('Failed to update.', r.message.data);
                    }

                }
            });
        });

    }


}