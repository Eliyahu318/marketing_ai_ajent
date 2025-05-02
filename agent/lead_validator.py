import re


def validate_lead(lead_info: dict) -> tuple[bool, str]:
    if len(lead_info.get("name", "").strip()) < 2:
        return False, "השם לא תקין"
    if not re.match(r"^05\d{8}$", lead_info.get("phone_number", "").strip()):
        return False, "מספר הנייד אינו תקין"
    if lead_info.get("business_sector", "").strip() == "":
        return False, "חסר תחום עיסוק"
    if lead_info.get("expectation", "").strip() == "":
        return False, "חסר ציפיות"
    else:
        return True, ""

