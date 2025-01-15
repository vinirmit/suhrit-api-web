from pymongo import MongoClient

def copy_database(source_uri, source_db_name, target_uri, target_db_name):
    source_client = MongoClient(source_uri)
    target_client = MongoClient(target_uri)

    source_db = source_client[source_db_name]
    target_db = target_client[target_db_name]

    for collection_name in ['counts', 'history', 'patients']:
        source_collection = source_db[collection_name]
        target_collection = target_db[collection_name]

        documents = source_collection.find()
        target_collection.insert_many(documents)

    source_client.close()
    target_client.close()

if __name__ == "__main__":
    source_uri = ""
    source_db_name = "suhrit-qa"
    target_uri = ""
    target_db_name = "suhrit-prod"

    copy_database(source_uri, source_db_name, target_uri, target_db_name)
