from datetime import datetime


def get_report(db, body):

    start_date, end_date = parse_dates(body['start_date'], body['end_date'])
    collection = db['history']

    # Define the aggregation pipeline
    pipeline = [{
        '$project': {
            '_id': 0,
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
            'totalKVisits': {'$size': "$matchedKVisits"}
        }
    }]

    total_sums = {
        "totalOpdPayments": 0,
        "totalKarmaPayments": 0,
        "totalVisits": 0,
        "totalKVisits": 0
    }
    
    for entry in list(collection.aggregate(pipeline)):
        total_sums["totalOpdPayments"] += entry["totalOpdPayments"]
        total_sums["totalKarmaPayments"] += entry["totalKarmaPayments"]
        total_sums["totalVisits"] += entry["totalVisits"]
        total_sums["totalKVisits"] += entry["totalKVisits"]
        
    return { "success": True, "payload": total_sums}

def parse_dates(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    return start_date, end_date




# pipeline = [
#         # Step 1: Perform a lookup on patients using the 'patientId' field
#         {
#             "$lookup": {
#                 "from": "patients",  # Name of the collection to join
#                 "localField": "patientId",  # Field from collectionA to match
#                 "foreignField": "patientId",  # Field from collectionB to match
#                 "as": "joinedData"  # Output array field from the lookup
#             }
#         },
#         # Step 2: Project only the necessary fields and filter the arrays by date range
#         {
#             "$project": {
#                 "_id": 0,  # Exclude _id if not needed
#                 "patientId": 1,
#                 "joinedData": 1,
#                 # Filter and map over visits to include the id in each item
#                 "visits": {
#                     "$map": {
#                         "input": {
#                             "$filter": {
#                                 "input": "$visits",
#                                 "as": "item",
#                                 "cond": {
#                                     "$and": [
#                                         # Start date
#                                         {"$gte": ["$$item.visitDate", start_date]},
#                                         # End date
#                                         {"$lte": ["$$item.visitDate", end_date]}
#                                     ]
#                                 }
#                             }
#                         },
#                         "as": "filteredItem",
#                         # Merge id into each item
#                         "in": {"$mergeObjects": ["$$filteredItem", {"patientId": "$patientId"}]}
#                     }
#                 },
#                 # Filter and map over kvisits to include the id in each item
#                 "kvisits": {
#                     "$map": {
#                         "input": {
#                             "$filter": {
#                                 "input": "$kvisits",
#                                 "as": "item",
#                                 "cond": {
#                                     "$and": [
#                                         # Start date
#                                         # Start date
#                                         {"$gte": ["$$item.visitDate", start_date]},
#                                         # End date
#                                         {"$lte": ["$$item.visitDate", end_date]}
#                                     ]
#                                 }
#                             }
#                         },
#                         "as": "filteredItem",
#                         # Merge id into each item
#                         "in": {"$mergeObjects": ["$$filteredItem", {"patientId": "$patientId"}]}
#                     }
#                 }
#             }
#         }
#     ]