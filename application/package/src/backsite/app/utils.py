from flask import request, jsonify
from typing import Dict

def requires(data_schema: Dict[str, type]):
    '''
    Decorator to specify what data is required for an endpoint
    and automatically handle invalid inputs
    '''
    def _requires(f):
        '''
        Receives pointer to decorated function
        '''
        def __requires(*args, **kwargs):
            data = request.get_json()
            # Validate that all required data keys exist
            for key in data_schema:
                if key not in data:
                    return {"success": False, "msg": f"Missing required key {key}"}, 400
                elif type(data[key]) != data_schema[key]:
                    return {"success": False, "msg": f"Expected {key} to be of type {str(data_schema[key].__name__)}"}, 400
                # Add required keys to kwargs
                kwargs[key] = data[key]
            # Call function
            return f(*args, **kwargs)
        # Return inner function
        return __requires
    # Return inner function
    return _requires
            