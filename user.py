
def get_details(db, username):
    item = db.users.find_one({ "username" :username }, {"username": 0, "tenantId" : 0})
    if item is not None and '_id' in item:
        del item['_id']
        return { "success": True, "user" : item}
    else: 
        return { "success": False }