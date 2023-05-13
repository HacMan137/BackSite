import re
from flask import request, jsonify
from typing import Dict, Callable, Tuple
from functools import wraps

def pattern(regex, failure_message = "", input = "", key = ""):
    '''
    Helper function for regex input validation
    '''
    if type(input) != str:
        return f"Expected {key} to be of type string"
    
    m = re.fullmatch(regex, input)

    if m is None:
        return f"{key} does not match the input requirements" if failure_message == "" else failure_message
    
    return True

def requires(data_schema: Dict[str, type | Tuple[Callable | str, ...]]):
    '''
    Decorator to specify what data is required for an endpoint
    and automatically handle invalid inputs
    FIXME: This function has a large cyclomatic complexity. We should try to simplify
    '''
    def _requires(f):
        '''
        Receives pointer to decorated function
        '''
        @wraps(f)
        def __requires(*args, **kwargs):
            data = request.get_json()
            # Validate that all required data keys exist
            for key in data_schema:
                # Check if key exists
                if key not in data:
                    return {"success": False, "msg": f"Missing required key {key}"}, 400
                # If a required key type is specified, check that the data type matches
                elif type(data_schema[key]) == type and type(data[key]) != data_schema[key]:
                    return {"success": False, "msg": f"Expected {key} to be of type {str(data_schema[key].__name__)}"}, 400
                # If a key validation function is given, check that it returns True
                elif type(data_schema[key]) == tuple:
                    # Check if first item in tuple is a function
                    if callable(data_schema[key][0]):
                        # If it is, use index 1:end as arguments
                        validation_function = data_schema[key][0]
                        validation_arguments = data_schema[key][1:]
                    else:
                        # If not, default to the pattern function and use all tuple items as arguments
                        validation_function = pattern
                        validation_arguments = data_schema[key]
                    # Execute the validation function
                    validation_result = validation_function(*validation_arguments, input=data[key], key=key)
                    if validation_result != True:
                        return {"success": False, "msg": validation_result}, 400
                # Add required keys to kwargs
                kwargs[key] = data[key]
            # Call function
            return f(*args, **kwargs)
        # Return inner function
        return __requires
    # Return inner function
    return _requires