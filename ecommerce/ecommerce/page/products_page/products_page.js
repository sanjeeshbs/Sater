frappe.pages['products-page'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'products page',
		single_column: true
	});
}