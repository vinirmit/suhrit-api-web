from datetime import datetime


def get_report(db, body):

    start_date, end_date = parse_dates(body['start_date'], body['end_date'])
    collection = db['history']

    # Define the aggregation pipeline
    pipeline = [{
        '$project': {
            '_id': 0,
            'patientId': 1,  # Include patientId in the projection
            'matchedVisits': {
                '$filter': {
                    'input': "$visits",
                    'as': "item",
                    'cond': {'$and': [
                        {'$gte': ["$$item.visitDate", start_date]},
                        {'$lte': ["$$item.visitDate", end_date]}
                    ]
                    }
                }
            },
            'matchedKVisits': {
                '$filter': {
                    'input': "$kvisits",
                    'as': "item",
                    'cond': {
                        '$and': [
                            {'$gte': ["$$item.visitDate", start_date]},
                            {'$lte': ["$$item.visitDate", end_date]}
                        ]
                    }
                }
            }
        }
    }, {
        '$project': {
            '_id': 0,
            'totalOpdPayments': {'$sum': "$matchedVisits.opdPayment"},
            'totalKarmaPayments': {'$sum': "$matchedKVisits.payment"},
            'totalVisits': {'$size': "$matchedVisits"},
            'totalKVisits': {'$size': "$matchedKVisits"},
            'kvisitsList': {
                '$map': {
                    'input': "$matchedKVisits",
                    'as': "kvisit",
                    'in': {
                        'patientId': "$patientId",  # Include patientId from the root document
                        'visitDate': "$$kvisit.visitDate",
                        'payment': "$$kvisit.payment",
                        'karms': "$$kvisit.karms"
                    }
                }
            }  # Include the list of matchedKVisits with patientId
        }
    }]

    total_sums = {
        "totalOpdPayments": 0,
        "totalKarmaPayments": 0,
        "totalVisits": 0,
        "totalKVisits": 0,
        "kvisitsList": []  # Initialize the list of kvisits
    }
    
    for entry in list(collection.aggregate(pipeline)):
        total_sums["totalOpdPayments"] += entry["totalOpdPayments"]
        total_sums["totalKarmaPayments"] += entry["totalKarmaPayments"]
        total_sums["totalVisits"] += entry["totalVisits"]
        total_sums["totalKVisits"] += entry["totalKVisits"]
        if start_date == end_date:
            total_sums["kvisitsList"].extend(entry["kvisitsList"])

    if start_date == end_date: 
        for item in total_sums["kvisitsList"]:
            patient_id = item['patientId']
            patient_details = db['patients'].find_one(
                    {'patientId': patient_id}, 
                    {'_id': 0, 'firstName': 1, 'lastName': 1})
            item['firstName'] = patient_details.get('firstName')
            item['lastName'] = patient_details.get('lastName')
            item['visitDate'] = item['visitDate'].strftime('%Y-%m-%d')

    print(total_sums)
    result = { "success": True, "payload": total_sums }
    
    return result

def parse_dates(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    return start_date, end_date
