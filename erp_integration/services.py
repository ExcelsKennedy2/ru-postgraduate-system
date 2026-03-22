from .models import FinanceRecord


def get_finance_clearance(student):
    """
    Mock ERP lookup for now.
    Later this can call a real external API.
    """
    record = FinanceRecord.objects.filter(student=student).first()

    if not record:
        return {
            "status": "pending",
            "reference": None,
            "comments": "No finance record found.",
        }

    return {
        "status": record.status,
        "reference": record.reference,
        "comments": record.comments,
    }