from datetime import datetime, date
import traceback

def add_to_queue(db, body):
    print("In add_to_queue", body)
    body['visitId'] = get_next_id(db, body['type'])
    body["visitDate"] = datetime.today().strftime('%Y-%m-%d')
    
    wip = db.wip.find_one({'patient.patientId': body['patient']['patientId'],
                            'type':body['type']})
    if wip is not None:
        return { "success": False, "message": "Patient Already on the queue"}

    if body['type'] == "visit":
        history = db.history.find_one({'patientId': body['patient']['patientId']})
    
        if history is not None:
            last_visit = history['visits'][0]
            body['profile'] = last_visit['profile']
            body['aasans'] = last_visit['aasans']
            body['karms'] = last_visit['karms']
            body['medicines'] = last_visit['medicines']
            body['pathya'] = last_visit['pathya']
            body['apathya'] = last_visit['apathya']
            body['lastVisitDate'] = last_visit['visitDate'].strftime('%Y-%m-%d')
        
        db.wip.insert_one(body)
    else: 
        obj = {
            'patient': body['patient'],
            'kvisitId': get_next_id(db, body['type']),
            'karms': {},
            'status': 10
        }
        db.wip.insert_one(body)

    return { "success": True, "message": "Patient added to OPD Queue"}
    
def get_queue(db):
    return_data = []
    for item in db.wip.find({}):
        del item['_id']
        return_data.append(item)
    return { "success": True, "payload": return_data}
    
def update_visit(db, body):
    
    try:
        db.wip.find_one_and_replace({'visitId': body['visitId']}, body)
        return { "success": True }
    except Exception as e:
        print(e)
        return { "success": False, "message": "Error Updating Visit" }

def process_visit(db, body):
    
    try:
        body['visitDate'] = datetime.strptime(body['visitDate'], "%Y-%m-%d")
        if body['type'] == 'kvisit':
            patientId = body['patient']['patientId']
            history = db.history.find_one({'patientId': patientId})
            del body['state']
            del body['patient']
            if history is not None:
                history['kvisits'].insert(0, body)
                db.history.find_one_and_replace({'patientId': patientId }, history)
                db.wip.delete_one({'visitId': body['visitId']})
            
            else:
                history = {}
                history['patientId'] = patientId
                history['visits'] = []
                history['kvisits'] = []
                history['kvisits'].append(body)
                db.history.insert_one(history)
                db.wip.delete_one({'visitId': body['visitId']})
    
        else:
            patientId = body['patient']['patientId']
            del body['lastVisitDate']
            del body['patient']
            history = db.history.find_one({'patientId': patientId})
            if history is not None:  
                history['visits'].insert(0, body)
                db.history.find_one_and_replace({'patientId': patientId }, history)
                db.wip.delete_one({'visitId': body['visitId']})
            
            else:
                history = {}
                history['patientId'] = patientId
                history['visits'] = []
                history['kvisits'] = []
                history['visits'].append(body)
                db.history.insert_one(history)
                db.wip.delete_one({'visitId': body['visitId']})
                
                

        return { "success": True }
    except Exception as e:
        print("Exception", e)
        traceback.print_exc() 
        return { "success": False, "message": "Error Updating Visit" }
        
def get_next_id(db, id_type):
    item = db.counts.find_one({"type": id_type})
    item['lastNumber'] = item['lastNumber'] + 1
    db.counts.find_one_and_replace({'_id': item['_id']}, item)
    return item['lastNumber']
    
def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))