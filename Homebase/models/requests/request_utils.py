from models.requests.requests import REQUESTS
from typing import Dict, Any, Tuple


def _object_from_args(name:str, args:Tuple[Any]) -> Any:
    return [arg for arg in args if arg.__class__.__name__ == name][0]

def get_request(request_name:str, r_type:str, *args) -> Dict[str, Any]:
    request_dict = REQUESTS[request_name][r_type].copy()

    for key, value in request_dict.items():
        func = value.split(".")

        object_to_use = _object_from_args(func[0], args)
        res = getattr(object_to_use, func[1])
        if callable(res):
            res = res()
        request_dict[key] = res

    return request_dict
