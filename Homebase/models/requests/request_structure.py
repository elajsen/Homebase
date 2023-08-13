from typing import Dict, Any


def structure_bills(bills_dict: Dict[str, Any], icons: Dict[str, str]) -> Dict[str, Any]:
    structured_bills = []
    for key, val in bills_dict.items():
        if key in ["_id", "data_time"] or len(val) == 0:
            continue
        structured_bills.append({
            "date": list(val.keys())[0],
            "page": key,
            "amount": list(val.values())[0],
            "icon": icons.get(key,"")
        })

    return structured_bills

def structure_week_category(week_categories: Dict[str, Any]) -> Dict[str, Any]:
    structured_week = []
    for key, val in week_categories.items():
        structured_week.append({
            "name": key,
            "value": round(val, 2)
        })
    return structured_week