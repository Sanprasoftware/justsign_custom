import frappe


ITEM_CODE = "Window Film Kit-CR-70-FWS"
SED_ITEM_CODE = "Window Film Kit-CR-70-SED"
SUV_ITEM_CODE = "Window Film Kit-CR-70-SUV"
WAREHOUSE = "Stores - JS"

SERIAL_REPLACEMENTS = {
	"DN-25-01049": ("3M-WFK00371", "3M-WFK00409"),
	"SINV-25-01177": ("3M-WFK00372", "3M-WFK00410"),
	"JS/15242/25-26": ("3M-WFK00701", "3M-WFK00750"),
	"DN-26-00420": ("3M-WFK01763", "3M-WFK01782"),
}

STALE_ACTIVE_SERIALS = ("3M-WFK01481", "3M-WFK01482")

SED_SERIAL_REPLACEMENTS = {
	"SINV-25-01177": ("3M-WFK00351", "3M-WFK00363"),
	"SINV-25-01037": ("3M-WFK00751", "3M-WFK00752"),
}

SUV_SERIAL_REPLACEMENTS = {
	"SINV-25-01280": ("3M-WFK00129", "3M-WFK00146"),
	"SINV-25-01361": ("3M-WFK00130", "3M-WFK00147"),
	"JS/15268/25-26": ("3M-WFK00131", "3M-WFK00148"),
	"DN-26-27-00290": ("3M-WFK00621", "3M-WFK00630"),
}


def _get_target_entry(voucher_no, old_serial_no, item_code=ITEM_CODE):
	rows = frappe.db.sql(
		"""
		select
			b.name as bundle,
			b.voucher_type,
			b.voucher_no,
			b.docstatus,
			b.type_of_transaction,
			e.name as entry,
			e.serial_no,
			e.qty,
			e.warehouse
		from `tabSerial and Batch Bundle` b
		inner join `tabSerial and Batch Entry` e on e.parent = b.name
		where b.item_code = %s
		and b.voucher_no = %s
		and b.docstatus = 1
		and b.type_of_transaction = 'Outward'
		and e.serial_no = %s
		""",
		(item_code, voucher_no, old_serial_no),
		as_dict=True,
	)
	if len(rows) != 1:
		frappe.throw(f"Expected 1 outward row for {voucher_no} / {old_serial_no}, found {len(rows)}")

	return rows[0]


def _get_outward_count(serial_no):
	return frappe.db.sql(
		"""
		select count(*)
		from `tabSerial and Batch Entry` e
		inner join `tabSerial and Batch Bundle` b on b.name = e.parent
		where e.serial_no = %s
		and b.docstatus = 1
		and b.type_of_transaction = 'Outward'
		""",
		serial_no,
	)[0][0]


@frappe.whitelist()
def preview_window_film_serial_correction():
	return _build_correction_plan()


@frappe.whitelist()
def apply_window_film_serial_correction():
	plan = _build_correction_plan()

	for row in plan["replacements"]:
		frappe.db.set_value("Serial and Batch Entry", row["entry"], "serial_no", row["new_serial_no"])
		frappe.db.set_value(
			"Serial No",
			row["new_serial_no"],
			{"status": "Delivered", "warehouse": None},
		)

	for serial_no in STALE_ACTIVE_SERIALS:
		frappe.db.set_value("Serial No", serial_no, {"status": "Delivered", "warehouse": None})

	frappe.db.commit()
	return _build_correction_summary()


@frappe.whitelist()
def preview_window_film_sed_serial_correction():
	return _build_correction_plan(
		item_code=SED_ITEM_CODE,
		serial_replacements=SED_SERIAL_REPLACEMENTS,
		stale_active_serials=(),
	)


@frappe.whitelist()
def apply_window_film_sed_serial_correction():
	plan = _build_correction_plan(
		item_code=SED_ITEM_CODE,
		serial_replacements=SED_SERIAL_REPLACEMENTS,
		stale_active_serials=(),
	)

	for row in plan["replacements"]:
		frappe.db.set_value("Serial and Batch Entry", row["entry"], "serial_no", row["new_serial_no"])
		frappe.db.set_value(
			"Serial No",
			row["new_serial_no"],
			{"status": "Delivered", "warehouse": None},
		)

	frappe.db.commit()
	return _build_correction_summary(SED_ITEM_CODE)


@frappe.whitelist()
def preview_window_film_suv_serial_correction():
	return _build_correction_plan(
		item_code=SUV_ITEM_CODE,
		serial_replacements=SUV_SERIAL_REPLACEMENTS,
		stale_active_serials=(),
	)


@frappe.whitelist()
def apply_window_film_suv_serial_correction():
	plan = _build_correction_plan(
		item_code=SUV_ITEM_CODE,
		serial_replacements=SUV_SERIAL_REPLACEMENTS,
		stale_active_serials=(),
	)

	for row in plan["replacements"]:
		frappe.db.set_value("Serial and Batch Entry", row["entry"], "serial_no", row["new_serial_no"])
		frappe.db.set_value(
			"Serial No",
			row["new_serial_no"],
			{"status": "Delivered", "warehouse": None},
		)

	frappe.db.commit()
	return _build_correction_summary(SUV_ITEM_CODE)


def _build_correction_plan(
	item_code=ITEM_CODE,
	serial_replacements=SERIAL_REPLACEMENTS,
	stale_active_serials=STALE_ACTIVE_SERIALS,
):
	replacements = []
	for voucher_no, (old_serial_no, new_serial_no) in serial_replacements.items():
		target = _get_target_entry(voucher_no, old_serial_no, item_code)
		new_serial = frappe.db.get_value(
			"Serial No", new_serial_no, ["item_code", "status", "warehouse"], as_dict=True
		)

		if not new_serial:
			frappe.throw(f"Replacement serial {new_serial_no} does not exist")
		if new_serial.item_code != item_code:
			frappe.throw(f"Replacement serial {new_serial_no} does not belong to {item_code}")
		if new_serial.status != "Active" or new_serial.warehouse != WAREHOUSE:
			frappe.throw(
				f"Replacement serial {new_serial_no} is not Active in {WAREHOUSE}: "
				f"{new_serial.status} / {new_serial.warehouse}"
			)

		outward_count = _get_outward_count(new_serial_no)
		if outward_count:
			frappe.throw(f"Replacement serial {new_serial_no} already has {outward_count} outward transaction(s)")

		replacements.append(
			{
				"voucher_no": voucher_no,
				"voucher_type": target.voucher_type,
				"bundle": target.bundle,
				"entry": target.entry,
				"old_serial_no": old_serial_no,
				"new_serial_no": new_serial_no,
			}
		)

	return {
		"item_code": item_code,
		"warehouse": WAREHOUSE,
		"replacements": replacements,
		"mark_delivered": list(stale_active_serials),
	}


def _build_correction_summary(item_code=ITEM_CODE):
	active_serials = frappe.get_all(
		"Serial No",
		filters={"item_code": item_code, "status": "Active", "warehouse": WAREHOUSE},
		pluck="name",
		order_by="name",
	)
	duplicate_outward = frappe.db.sql(
		"""
		select e.serial_no, count(*) as outward_count
		from `tabSerial and Batch Entry` e
		inner join `tabSerial and Batch Bundle` b on b.name = e.parent
		where e.serial_no in (
			select name from `tabSerial No` where item_code = %s
		)
		and b.docstatus = 1
		and b.type_of_transaction = 'Outward'
		group by e.serial_no
		having count(*) > 1
		order by e.serial_no
		""",
		item_code,
		as_dict=True,
	)
	return {"active_serials": active_serials, "duplicate_outward": duplicate_outward}
