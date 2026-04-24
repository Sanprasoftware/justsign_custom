
frappe.ui.form.on('Documentation', {
    refresh(frm) {
        // frappe.throw("Hii")
        if (!window.doc_password_verified) {
            show_password_popup();
        }
    },
    onload(frm) {
        frappe.throw("Hii")
        if (!window.doc_password_verified) {
            show_password_popup();
        }
    }
});

function show_password_popup() {

    let d = new frappe.ui.Dialog({
        title: "Enter Password",
        fields: [
            {
                label: "Password",
                fieldname: "password",
                fieldtype: "Password",
                reqd: 1
            }
        ],
        primary_action_label: "Submit",
        primary_action(values) {

            frappe.call({
                method: "verify_company_password",
                args: {
                    password: values.password
                },
                freeze: true,
                callback: function(r) {

                    if (r.message === true) {
                        window.doc_password_verified = true;
                        d.hide();

                    } else {
                        frappe.msgprint({
                            title: "Error",
                            message: "Enter correct password",
                            indicator: "red"
                        });

                        d.set_value("password", "");
                    }
                }
            });
        }
    });

    // Disable closing
    d.$wrapper.find(".modal-header .close").hide();
    d.$wrapper.find(".modal-footer .btn-secondary").hide();

    d.show();
}frappe.router.on('change', () => {
    const route = frappe.get_route();

    // Check for Documentation List or Form
    if (
        (route[0] === "List" && route[1] === "Documentation") ||
        (route[0] === "Form" && route[1] === "Documentation")
    ) {
        if (!window.doc_password_verified) {
            show_password_popup();
        }
    }
});


function show_password_popup() {

    let d = new frappe.ui.Dialog({
        title: "Enter Password",
        size: "large",
        static: true,  // ❌ no outside click close

        fields: [
            {
                label: "Password",
                fieldname: "password",
                fieldtype: "Data",
                reqd: 1
            }
        ],

        primary_action_label: "Submit",
        primary_action(values) {

            frappe.call({
                method: "justsign_custom.public.py.password.verify_company_password",
                args: {
                    password: values.password
                },
                freeze: true,
                callback: function(r) {

                    if (r.message === true) {
                        window.doc_password_verified = true;
                        d.hide();

                    } else {
                        frappe.msgprint({
                            title: "Error",
                            message: "Enter correct password",
                            indicator: "red"
                        });

                        d.set_value("password", "");
                    }
                }
            });
        }
    });

    d.show();

    // 🔐 Password mask
    d.fields_dict.password.$input.attr("type", "password");

    // 🔥 WIDTH = 60%
    d.$wrapper.find('.modal-dialog').css({
        "max-width": "60%",
        "width": "60%"
    });

    // 🔥 HEIGHT + CENTER ALIGN
    d.$wrapper.find('.modal-dialog').css({
        "display": "flex",
        "align-items": "center",
        "min-height": "100vh"   // full vertical center
    });

    d.$wrapper.find('.modal-content').css({
        "height": "60vh",       // 👈 increase height here
        "display": "flex",
        "flex-direction": "column",
        "justify-content": "center"
    });

    // ❌ Disable close options
    d.$wrapper.find(".modal-header .close").hide();
    d.$wrapper.find(".modal-footer .btn-secondary").hide();

    // ❌ Disable ESC
    d.$wrapper.on('keydown', function(e) {
        if (e.key === "Escape") {
            e.preventDefault();
        }
    });
}