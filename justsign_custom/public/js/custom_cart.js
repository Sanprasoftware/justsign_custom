frappe.provide("justsign_custom.cart");

frappe.ready(function () {
    if (window.location.pathname !== "/cart") {
        return;
    }

    justsign_custom.cart.inject_freight_fields();
    justsign_custom.cart.load_uom_controls();
    justsign_custom.cart.check_profile_popup();
    justsign_custom.cart.override_cart_update();
});

justsign_custom.cart.override_cart_update = function () {
    webshop.webshop.shopping_cart.shopping_cart_update = function(args) {
        const $row = $(`[data-item-code="${args.item_code}"]`).closest("tr");
        const uom = $row.find(".cart-uom").val();

        frappe.call({
            method: "justsign_custom.public.py.web_cart.update_cart",
            args: {
                item_code: args.item_code,
                qty: args.qty,
                additional_notes: args.additional_notes,
                uom: uom,
                shipper: $(".custom-cart-shipper").val(),
                mode: $(".custom-cart-mode").val(),
                with_items: 1
            },
            callback: function(r) {
                if (!r.exc) {
                    $(".cart-items").html(r.message.items);
                    $(".cart-tax-items").html(r.message.total);
                    $(".payment-summary").html(r.message.taxes_and_totals);
                    webshop.webshop.shopping_cart.set_cart_count();
                    justsign_custom.cart.load_uom_controls();
                    justsign_custom.cart.inject_freight_fields();

                    if (args.cart_dropdown !== true) {
                        $(".cart-icon").hide();
                    }
                }
            }
        });
    };
};

justsign_custom.cart.inject_freight_fields = function () {
    if ($(".custom-cart-freight").length) {
        return;
    }

    $(".payment-summary").before(`
        <div class="custom-cart-freight mb-4">
            <label>${__("Shipper")}</label>
            <div class="custom-cart-shipper-wrapper position-relative">
                <input type="text" class="form-control custom-cart-shipper-search" autocomplete="off">
                <input type="hidden" class="custom-cart-shipper">
                <div class="custom-cart-shipper-options border bg-white w-100" style="display: none; position: absolute; z-index: 1050; max-height: 220px; overflow-y: auto;"></div>
            </div>
            <label class="mt-2">${__("Mode")}</label>
            <select class="form-control custom-cart-mode">
                <option value=""></option>
                <option value="Air">Air</option>
                <option value="Road">Road</option>
            </select>
        </div>
    `);

    frappe.call({
        method: "justsign_custom.public.py.web_cart.get_cart_freight_options",
        callback: function(r) {
            const data = r.message || {};
            justsign_custom.cart.render_shipper_options(data.shippers || []);
            $(".custom-cart-shipper").val(data.shipper || "");
            $(".custom-cart-shipper-search").val(data.shipper || "");
            $(".custom-cart-mode").val(data.mode || "");
        }
    });

    $(".custom-cart-shipper-search").on("focus", function () {
        $(".custom-cart-shipper-options").show();
    });

    $(".custom-cart-shipper-search").on("input", frappe.utils.debounce(function () {
        const txt = $(this).val();
        $(".custom-cart-shipper").val("");

        frappe.call({
            method: "justsign_custom.public.py.web_cart.search_supplier_options",
            args: {
                txt: txt
            },
            callback: function (r) {
                justsign_custom.cart.render_shipper_options(r.message || []);
                $(".custom-cart-shipper-options").show();
            }
        });
    }, 250));

    $(".custom-cart-shipper-options").on("mousedown", ".custom-cart-shipper-option", function () {
        const name = $(this).data("name");
        const label = $(this).text();

        $(".custom-cart-shipper").val(name);
        $(".custom-cart-shipper-search").val(label);
        $(".custom-cart-shipper-options").hide();
        justsign_custom.cart.set_freight_options();
    });

    $(".custom-cart-shipper-search").on("blur", function () {
        setTimeout(() => $(".custom-cart-shipper-options").hide(), 200);
    });

    $(".custom-cart-mode").on("change", function () {
        justsign_custom.cart.set_freight_options();
    });
};

justsign_custom.cart.render_shipper_options = function (shippers) {
    const options_html = shippers.map(shipper => {
        const name = frappe.utils.escape_html(shipper.name);
        const label = frappe.utils.escape_html(shipper.label || shipper.name);
        return `<div class="custom-cart-shipper-option px-3 py-2" data-name="${name}" style="cursor: pointer;">${label}</div>`;
    }).join("");

    $(".custom-cart-shipper-options").html(options_html || `<div class="px-3 py-2 text-muted">${__("No results found")}</div>`);
};

justsign_custom.cart.set_freight_options = function () {
    frappe.call({
        method: "justsign_custom.public.py.web_cart.set_cart_freight_options",
        args: {
            shipper: $(".custom-cart-shipper").val(),
            mode: $(".custom-cart-mode").val()
        },
        callback: function (r) {
            if (!r.exc) {
                $(".cart-tax-items").html(r.message.total);
                $(".payment-summary").html(r.message.taxes_and_totals);
            }
        }
    });
};

justsign_custom.cart.load_uom_controls = function () {
    frappe.call({
        method: "justsign_custom.public.py.web_cart.get_cart_uom_data",
        callback: function (r) {
            const data = r.message || {};

            Object.keys(data).forEach(item_code => {
                const $qty = $(`.cart-qty[data-item-code="${item_code}"]`);
                if (!$qty.length || $qty.closest("td").find(".cart-uom").length) {
                    return;
                }

                const html = data[item_code].uoms.map(row => {
                    const selected = row.uom === data[item_code].selected_uom ? "selected" : "";
                    const escaped_uom = frappe.utils.escape_html(row.uom);
                    return `<option value="${escaped_uom}" ${selected}>${escaped_uom}</option>`;
                }).join("");

                $qty.closest("td").append(`<select class="form-control cart-uom mt-2">${html}</select>`);
            });

            $(".cart-uom").off("change").on("change", function () {
                const $row = $(this).closest("tr");
                const item_code = $row.find(".cart-qty").data("item-code");
                const qty = $row.find(".cart-qty").val();
                webshop.webshop.shopping_cart.shopping_cart_update({ item_code, qty });
            });
        }
    });
};

justsign_custom.cart.check_profile_popup = function () {
    frappe.call({
        method: "justsign_custom.public.py.web_cart.get_profile_status",
        callback: function (r) {
            if (r.message && r.message.required) {
                justsign_custom.cart.show_profile_popup();
            }
        }
    });
};

justsign_custom.cart.show_profile_popup = function () {
    const dialog = new frappe.ui.Dialog({
        title: __("Complete Profile"),
        fields: [
            { fieldtype: "Data", fieldname: "mobile_no", label: __("Mobile Number"), reqd: 1 },
            { fieldtype: "Check", fieldname: "has_gst", label: __("I have valid GST Number") },
            {
                fieldtype: "Data",
                fieldname: "gst_number",
                label: __("GST Number"),
                depends_on: "eval:doc.has_gst",
                mandatory_depends_on: "eval:doc.has_gst"
            },
            { fieldtype: "Data", fieldname: "address_line1", label: __("Address Line 1"), reqd: 1 },
            { fieldtype: "Data", fieldname: "city", label: __("City"), reqd: 1 },
            { fieldtype: "Data", fieldname: "state", label: __("State"), reqd: 1 },
            { fieldtype: "Link", fieldname: "country", label: __("Country"), options: "Country", reqd: 1 },
            { fieldtype: "Data", fieldname: "pincode", label: __("Pincode"), reqd: 1 },
        ],
        primary_action_label: __("Save"),
        primary_action(values) {
            frappe.call({
                method: "justsign_custom.public.py.web_cart.save_profile_popup",
                args: { data: values },
                callback: function () {
                    dialog.hide();
                    frappe.show_alert(__("Profile saved"));
                    location.reload();
                }
            });
        }
    });

    dialog.show();
};
