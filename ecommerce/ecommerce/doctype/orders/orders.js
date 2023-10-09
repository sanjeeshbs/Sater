// Copyright (c) 2021, Sanjeesh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Orders', {


	setup: function (frm) {
		frm.fields_dict["items"].grid.get_field("unit_name").get_query = function (doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				query: "ecommerce.ecommerce.doctype.orders.orders.get_item_units",
				filters: { 'item': d.item }
			}
		},
			frm.fields_dict["time_slote"].get_query = function (doc) {
				return {
					query: "ecommerce.ecommerce.doctype.orders.orders.get_time_slotes"
				}
			},

			frm.fields_dict["shipping_address"].get_query = function (doc) {
				console.log('called');
				return {
					query: "ecommerce.ecommerce.doctype.orders.orders.get_shipping_address",
					filters: { 'customer': doc.customer }
				}
			}


	},


	// customer(frm) {
	// 	frm.set_df_property("shipping_address", "options", []);
	// 	if (!frm.doc.customer) {
	// 		return;
	// 	}

	// 	frappe.call({
	// 		method: "ecommerce.ecommerce.doctype.orders.orders.get_shipping_address",
	// 		args: {
	// 			customer: frm.doc.customer
	// 		},
	// 		callback: function (r) {
	// 			if (r.message) {
	// 				console.log('DATA:', r.message);
	// 				let address_list = r.message.map(function (address, index) {
	// 					return address.address;
	// 				});

	// 				frm.set_df_property("shipping_address", "options", address_list);
	// 				cur_frm.refresh_field("items");
	// 			}
	// 		}
	// 	})

	// }

});

frappe.ui.form.on('OrderDetails', {
	items_remove(frm, cdt, cdn) {
		update_grand_total(frm);
	},
	item(frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn);
		row.unit_name = '';
		row.qty = 1;
		row.unit_price = 0.000;
		row.vat = 0.000;
		row.total_price = 0.000;
		cur_frm.refresh_field("items");
	},
	unit_name(frm, cdt, cdn) {
		update_item_name(frm, cdt, cdn);
		update_total(frm, cdt, cdn);
	},
	qty(frm, cdt, cdn) {
		update_total(frm, cdt, cdn);
	},


});

// frappe.ui.form.on("Expense Claim Detail", "validate", function(frm, dt, dn) 
// { var row = locals[dt][dn]; 
// 	frappe.model.set_value(dt, dn, "claim_amount", 
// 	flt(row.qte * row.prix_unitaire)); 
// 	refresh_field("expenses"); 
// });



function update_item_name(frm, cdt, cdn) {
	let row = frappe.get_doc(cdt, cdn);
	console.log('called:', row.item);
	frappe.call({
		method: "ecommerce.ecommerce.doctype.orders.orders.get_item_details",
		args: {
			item: row.item,
			unit: row.unit_name
		},
		callback: function (r) {
			if (r.message) {
				frappe.model.set_value(cdt, cdn, 'item_name', r.message[0].item_name);
				frappe.model.set_value(cdt, cdn, 'barcode', r.message[0].barcode);
				cur_frm.refresh_field("items");
			}
		}
	})
}

function update_grand_total(frm) {
	let total_amt = 0;
	let total_vat = 0;
	frm.doc.items.forEach(function (d) { total_amt += d.total_price; total_vat += d.vat; });
	frm.set_value('amount', total_amt);
	frm.set_value('vat', total_vat);
	frm.set_value('total_amount', total_amt + total_vat);
}



function update_total(frm, cdt, cdn) {
	let row = frappe.get_doc(cdt, cdn);
	frappe.call({
		method: "ecommerce.ecommerce.doctype.orders.orders.get_item_details",
		args: {
			item: row.item,
			unit: row.unit_name
		},
		callback: function (r) {
			if (r.message) {
				const unit_price = r.message[0].price;
				const vat_value = r.message[0].vat_value;

				let total_price = row.qty * unit_price;
				let total_vat = (total_price * (vat_value / 100.0));

				frappe.model.set_value(cdt, cdn, 'unit_price', unit_price);
				frappe.model.set_value(cdt, cdn, 'vat', total_vat)
				frappe.model.set_value(cdt, cdn, 'total_price', total_price)

				cur_frm.refresh_field("items");
				update_grand_total(frm);
			}
		}
	})
}