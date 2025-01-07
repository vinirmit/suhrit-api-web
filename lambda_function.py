import os 
import boto3
import json
import pymongo
from patient import search_patient, edit_patient, patient_history, register_patient, patient_last_visit
from visit import add_to_queue, get_queue, update_visit, process_visit
from util import get_med_list, get_tag_list
from report import get_report 

#https://www.linkedin.com/pulse/add-external-python-libraries-aws-lambda-using-layers-gabe-olokun/
print('Loading function')
DB_URL = (os.environ['instance']).replace("<password>", os.environ['key'])
print(DB_URL)
client = pymongo.MongoClient(DB_URL)
print(client)
db = client.suhrit

def lambda_handler(event, context):

    # Initialize response variables
    request_body = {}
    status_code = 200

    # Check if the 'body' key exists and is not None
    if 'body' in event and event['body']:
        # Get the request body
        request_body = event['body']
        
        # Check if the body is Base64 encoded
        if event.get('isBase64Encoded'):
            request_body = base64.b64decode(request_body).decode('utf-8')

        # Parse the body if it's JSON
        try:
            request_body = json.loads(request_body)
            print(request_body)
            response_body = {'message': 'Request processed successfully', 'data': request_body}
        except json.JSONDecodeError:
            # Handle JSON parsing errors
            response_body = {'error': 'Invalid JSON format in request body'}
            status_code = 400
    
    print("Received body:", json.dumps(request_body, indent=2))
    path_dict = {
        "/patient/search": search_patient,
        "/patient/edit": edit_patient,
        "/patient/history": patient_history,
        "/patient/lastvisit": patient_last_visit,
        "/patient/register": register_patient,
        "/visit/add": add_to_queue,
        "/visit/update": update_visit,
        "/visit/process": process_visit,
        "/visit/queue": get_queue,
        "/report/default": get_report,
        "/util/medlist": get_med_list,
        "/util/taglist": get_tag_list
    }
    
    path = event.get('path')
    path = path.replace("/default/drdigi","")
    print("Received Path:", path)
    # Retrieve the function from the dictionary
    func = path_dict.get(path)

    # Check if the function exists
    if func:
        # Call the function with parameters
        if (path == "/patient/search"
            or path == "/patient/edit"
            or path == "/patient/register"
            or path == "/patient/lastvisit"
            or path == "/report/default" 
            or path == "/visit/add" 
            or path == "/visit/update"
            or path == "/visit/process"
            or path == "/patient/history"):
            result = func(db, request_body)
            print(result)
        elif (path == "/visit/queue" 
              or path == "/util/medlist"
              or path == "/util/taglist"):
            result = func(db)
        else:
            result = { "success": False, "message": "Path not found"}
    else:
        result = { "success": False, "message": "Function not found"}

    # Return response
    # respond(None, result)
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }



    