import os 
import boto3
import json
import base64
import pymongo
from patient import search_patient, edit_patient, patient_history, register_patient, patient_last_visit
from visit import add_to_queue, get_queue, update_visit, process_visit
from util import get_med_list, get_tag_list
from user import get_details
from report import get_report 

#https://www.linkedin.com/pulse/add-external-python-libraries-aws-lambda-using-layers-gabe-olokun/
DB_URL = (os.environ['instance']).replace("<password>", os.environ['key']).replace("<user>", os.environ['user'])
# DB_URL = DB_URL.replace("<user>", os.environ['user'])
client = pymongo.MongoClient(DB_URL)
db = client[os.environ['DB_NAME']]

cached_users = {} 

def lambda_handler(event, context):

    global db, cached_users
    # Initialize response variables
    request_body = {}
    status_code = 200

    # user_email = get_user_email(event['headers'].get('authorization').split(" ")[1])
    token = decode_jwt(event['headers'].get('authorization').split(" ")[1])
    username = token['username']
    if username not in cached_users:
        user_det = get_details(db, username)
        if (user_det['success']):
            cached_users[username] = user_det['user']
        else:
            result = { "success": False, "message": "User not found"}
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }

    user = cached_users[username]
    print("user: ", user)

    path = event.get("path") or event.get("rawPath") or event.get("requestContext", {}).get("http", {}).get("path")
    path = path.replace("/default","")

    if path == "/user/details":
        result = { "success": True, "user": user }
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }

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
        "/report/range": get_report,
        "/util/medlist": get_med_list,
        "/util/taglist": get_tag_list
    }
    
    
    # Retrieve the function from the dictionary
    func = path_dict.get(path)

    # Check if the function exists
    if func:
        # Call the function with parameters
        if (path == "/patient/search"
            or path == "/patient/edit"
            or path == "/patient/register"
            or path == "/patient/lastvisit"
            or path == "/report/range" 
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


# def get_user_email(access_token):
#     client = boto3.client('cognito-idp')
    
#     try:
#         response = client.get_user(
#             AccessToken=access_token
#         )

#         print("Response: ",response)
#         for attribute in response['UserAttributes']:
#             if attribute['Name'] == 'email':
#                 return attribute['Value']
#     except client.exceptions.NotAuthorizedException:
#         print("The access token is invalid or expired.")
#         return None
#     except client.exceptions.UserNotFoundException:
#         print("The user does not exist.")
#         return None
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None

#     return None

def decode_jwt(token):
    # Split the JWT token into its three parts (header, payload, signature)
    parts = token.split(".")
    
    if len(parts) != 3:
        raise ValueError("Invalid JWT token format")
    
    # Decode the payload (the second part of the token)
    payload_encoded = parts[1]
    
    # Add padding if necessary to ensure the base64 string is valid
    padding = "=" * ((4 - len(payload_encoded) % 4) % 4)
    payload_encoded += padding
    
    try:
        # Decode from Base64 URL-safe encoding and convert to JSON
        decoded_bytes = base64.urlsafe_b64decode(payload_encoded)
        decoded_payload = json.loads(decoded_bytes.decode("utf-8"))
        return decoded_payload
    except Exception as e:
        raise ValueError(f"Error decoding JWT token: {str(e)}")