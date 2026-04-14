// let installer = []

// function add_foundry_filter(frm) {
//     if (frm.doc.customer) {
//         frm.call({
//             method: "justsign_custom.public.py.sales_order.add_installer_filter",
//             args: {
//                 customer: frm.doc.customer,
//             },
//             callback: function(r) {
//                 if (r.message) {
//                     installer = r.message;

//                     // apply filter on child table link field
//                     frm.set_query("user", "custom_installer_", () => {
//                         return {
//                             filters: {
//                                     name: ["in", installer]   
//                                 }

//                         }
//                     });  
//                 }
//             }
//         });
//     }
// }

// frappe.ui.form.on("Sales Order", {
//     onload_post_render: function(frm){
//         add_foundry_filter(frm)
//     },
//     customer:async function(frm) {
//         await add_foundry_filter(frm)  

//     },
// })
