from typing import Dict, Any


def compare_dicts(dict1: Dict[Any, Any], dict2: Dict[Any, Any]):
    for key in dict1.keys():
        if key not in dict2.keys():
            raise Exception(f"key: {key} in dict1 doesnt exist in dict2")
        
    for key in dict2.keys():
        if key not in dict1.keys():
            raise Exception(f"key: {key} in dict1 doesnt exist in dict2")

    for key in dict1.keys():
        if dict1[key] != dict2[key]:
            raise Exception(f"Key: {key}\nValue: {dict1[key]} in dict1 is not the same as {dict2[key]} in dict2")