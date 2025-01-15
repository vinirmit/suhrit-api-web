from datetime import datetime, date

def get_static_data():
    return "Patient API"
    
def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    
def search_patient(db, body):

    item = db.patients.find_one(body)
    if item is not None and '_id' in item:
        item['age']= calculate_age(item['dateofbirth'])
        item['dateofbirth'] = item['dateofbirth'].strftime('%Y-%m-%d')
        del item['_id']
        return { "success": True, "payload": item}
    else:
        return { "success": False, "message": "Patient Not Found"}
        
def register_patient(db, body):

    patient = body['patient']
    payment = body['payment']
    patient['dateofbirth'] = datetime.strptime(patient['dateofbirth'], "%Y-%m-%d")
    
    try: 
        patient['patientId'] = get_next_id(db,"patient")
        db.patients.insert_one(patient)
        if payment ==  0:
            return { "success": True, "message": "Patient Registered" }
        
        del patient['_id']
        visitId = get_next_id(db, "visit")
        patient['age'] = calculate_age(patient['dateofbirth'])
        del patient['dateofbirth']
        queue_data = {
            'visitId': visitId,
            'visitDate': datetime.today().strftime('%Y-%m-%d'),
            'type': 'visit',
            'opdPayment': 150,
            'patient': patient
        }
        
        db.wip.insert_one(queue_data)
        return { "success": True, "message": "Patient Registered" }
    except Exception as e:
        print(e)
        return { "success": False, "message": "Patient Not Registered" }
 
def edit_patient(db, body):

    patient = body['patient']
    patient['dateofbirth'] = datetime.strptime(patient['dateofbirth'], "%Y-%m-%d")
    
    try:        
        db.patients.find_one_and_replace({'patientId': patient['patientId']}, patient)
        return { "success": True, "message": "Patient Saved" }
    except Exception as e:
        print(e)
        return { "success": False, "message": "Patient Not Saved" }

def patient_last_visit(db, body):
    
    try:
        item = db.history.find_one({'patientId': body['patientId']})
        
        if item is None:
            return { "false": True, "message": "No Previous Visits found"}
            
        if len(item['visits']) == 0:
            return { "false": True, "message": "No Previous OPD Visits found"}
     
        payload = item["visits"][0]
        patient = db.patients.find_one({'patientId': body['patientId']}, {'_id': 0, 'dateofbirth': 0})
        payload['patient'] = patient
        payload['visitDate']= payload['visitDate'].strftime('%Y-%m-%d')
        return { "success": True, "payload": payload}
    except Exception as e:
        return { "success": False, "message": e}       

def patient_history(db, body):
    
    try:
        item = db.history.find_one({'patientId': body['patientId']})
        
        if item is not None:
            del item['_id']
            for vis in item['visits']:
                vis['visitDate'] = vis['visitDate'].strftime('%Y-%m-%d')
            for vis in item['kvisits']:
                vis['visitDate'] = vis['visitDate'].strftime('%Y-%m-%d')    
            return { "success": True, "payload": item}
        
        blank_hist = {
            'visits' : [],
            'kvisits' : []
        }
        
        return { "success": True, "payload": blank_hist}
    except Exception as e:
        return { "success": False, "message": e}

def get_next_id(db, id_type):
    item = db.counts.find_one({"type": id_type})
    item['lastNumber'] = item['lastNumber'] + 1
    db.counts.find_one_and_replace({'_id': item['_id']}, item)
    return item['lastNumber']
    
