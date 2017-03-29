from django.http import JsonResponse as JR


def JsonResponse(data={}, **kwargs):
    """
        response = {
            "data": {
                "user_ids": [1, 2, 3],
            },
            "error": {
                "return_code": "",
                "return_msg": ""
            }
        }
    """
    response = {"data": data}
    if kwargs.get("error"):
        error_dict = kwargs.get("error")

        if isinstance(error_dict, dict):
            error_dict = list(error_dict.items())
            response["error"] = {
                "return_code": error_dict[0][0],
                "return_msg": error_dict[0][1]
            }
        else:
            response["error"] = {
                "return_code": error_dict.return_code,
                "return_msg": error_dict.return_msg
            }
    return JR(response)
