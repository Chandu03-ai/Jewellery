from Razor_pay.Database.db import invoiceCollection

def insertInvoiceToDb(invoiceData: dict):
    """
    Insert a new invoice into the invoice collection.
    """
    try:
        result = invoiceCollection.insert_one(invoiceData)
        return str(result.inserted_id)
    except Exception as e:
        raise Exception(f"Failed to insert invoice: {e}")

def getInvoiceFromDb(query: dict): 
    """
    Retrieve an invoice by its ID.
    """
    try:
        invoice = invoiceCollection.find_one(query)
        if invoice and "_id" in invoice:
            invoice["_id"] = str(invoice["_id"])
        return invoice
    except Exception as e:
        raise Exception(f"Failed to fetch invoice by ID: {e}")

def getAllInvoicesFromDb(query: dict = {}):
    try:
        return [{k: v for k, v in invoice.items() if k != "_id"} for invoice in invoiceCollection.find(query)]
    except Exception as e:
        raise Exception(f"Failed to fetch all invoices: {e}")

def updateInvoiceData(query: dict, updatedInvoice: dict):
    """
    Upsert invoice: Updates if it exists, inserts if not.
    Returns 'updated' or 'inserted' based on operation result.
    """
    try:
        result = invoiceCollection.update_one(
            query,
            {"$set": updatedInvoice},
            upsert=True
        )
        status = "updated" if result.matched_count > 0 else "inserted"
        return {
            "status": status,
            "invoiceId": updatedInvoice.get("invoiceId")
        }
    except Exception as e:
        raise Exception(f"Failed to update or insert invoice: {e}")

def deleteInvoice(invoiceId: str):
    """
    Delete an invoice by its ID.
    """
    try:
        result = invoiceCollection.delete_one({"invoiceId": invoiceId})
        if result.deleted_count > 0:
            return True
        return False
    except Exception as e:
        raise Exception(f"Failed to delete invoice: {e}")