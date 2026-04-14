 frappe.ui.form.on('Custom Bundle Item', {
    item_code(frm, cdt, cdn) {
      frm.fields_dict.custom_items_bundle.grid.get_field('batch').get_query =
  function(doc, cdt, cdn) {
        const row = locals[cdt][cdn];
        return { filters: { item: row.item_code } };
      };
    }
  });