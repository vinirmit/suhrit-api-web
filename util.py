from datetime import datetime, date


def get_med_list(db):
    
    list = db.history.distinct("visits.medicines.name")
    return { "success": True, "payload": list}

def get_tag_list(db):
    
    readings = ['मधुमेह', 'रक्तचाप' ,'लक्षण/चिन्ह', 'प्रयोगशाला संबंधी', 'पूर्व निदान', 'उपद्रव', 'Weight']
    return_data = {}
    return_data['tags'] = db.history.distinct("visits.profile.tags")
    # return_data.extend(db.history.distinct("visits.profile.tags"))

    for read in readings:
        return_data[read] =db.history.distinct("visits.profile.readings." + read)

    return { "success": True, "payload": return_data}