frappe.ui.form.on('Purchase Invoice', {
    onload_post_render: async function(frm) {
        if (frm.is_new() && !frm.__posting_date_cleared) {
            frm.__posting_date_cleared = true;
            frm.set_df_property('posting_date', 'hidden', 0);
            await frm.set_value('set_posting_time', 1);
            await frm.set_value('posting_date', '');
            frm.set_df_property('posting_date', 'read_only', 0);
            frm.refresh_field('posting_date');
        }
    },
});
