from frappe.model.document import Document
from frappe.utils import add_months, getdate


class BookPackage(Document):
    def validate(self):
        if not self.valid_till:
            creation_date = getdate(self.creation)
            self.valid_till = add_months(creation_date, 12)
            self.status = "Active"
