from rest_framework.response import Response
from rest_framework import status as drf_status

def success_response(data,code):
    return Response({
        'isSuccess':True,
        'code':code,
        'data':data,
        'status_code':drf_status.HTTP_200_OK
    })

def flatten_errors(error_dict):
    messages = []
    if isinstance(error_dict, dict):
        for value in error_dict.values():
            if isinstance(value, list):
                messages.extend(value)
            elif isinstance(value, dict):
                messages.extend(flatten_errors(value))
    elif isinstance(error_dict, list):
        messages.extend(error_dict)
    else:
        messages.append(str(error_dict))
    return messages

def error_response(message, status_code):
    if isinstance(message, dict):
        message = flatten_errors(message)
    return Response({
        'isSuccess': False,
        'code': message,
        'status_code': status_code
    }, status=status_code)

def validation_error_response(errors,status_code):
    response_data = {"isSuccess": False, "code": errors,"status_code":status_code}
    return Response(response_data, status=status_code)