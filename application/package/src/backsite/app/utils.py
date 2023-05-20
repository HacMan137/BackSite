import re
import pika
import os
import json
import sys
from flask import request, jsonify
from typing import Dict, Callable, Tuple
from functools import wraps
from traceback import print_exc
from datetime import datetime

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
LOGFILE = "/var/log/backsite.log"

PASSWORD_REGEX = r'^.{8,}$'
EMAIL_REGEX = r'^\w+@\w+\.\w{1,}$'
USERNAME_REGEX = r'^.{6,}$'

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

def requires(data_schema: Dict[str, type | Tuple[Callable | str, ...]], optional=False):
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
                    if not optional:
                        return {"success": False, "msg": f"Missing required key {key}"}, 400
                    else:
                        data[key] = ""
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

def optional(data_schema: Dict[str, type | Tuple[Callable | str, ...]]):
    return requires(data_schema, optional=True)

def send_rabbitmq_message(data, queue_name):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        channel.queue_declare(queue=queue_name)

        channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(data))
        print(f"Sent data through queue {queue_name}. Data sent: {data}")
        connection.close()
    except Exception as e:
        print(f"Error while trying to send message to RabbitMQ: {e}")
        print_exc()
        sys.stdout.flush()
        return False
    
    return True

def log(content):
    line = f"{datetime.utcnow().isoformat()}\t{content}\n"
    with open(LOGFILE, "a") as f:
        f.write(line)