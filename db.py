import re

from pymongo import MongoClient
from config import MONGO_DB_URI

client = MongoClient(MONGO_DB_URI)
db = client["autofilter_db"]
files = db.files
channel_index_state = db.channel_index_state

def add_file(file_info):
    files.replace_one({"file_id": file_info["file_id"]}, file_info, upsert=True)

def search_files(query):
    literal_query = re.escape(query)
    return list(files.find(
        {"$or": [
            {"file_name": {"$regex": literal_query, "$options": "i"}},
            {"caption": {"$regex": literal_query, "$options": "i"}}
        ]}
    ))

def get_file_by_id(doc_id):
    from bson.objectid import ObjectId
    return files.find_one({"_id": ObjectId(doc_id)})

def file_count():
    return files.count_documents({})

def get_channel_backfill_cursor(channel_id):
    state = channel_index_state.find_one({"_id": str(channel_id)})
    return state["last_message_id"] if state else 0

def set_channel_backfill_cursor(channel_id, message_id):
    channel_index_state.update_one(
        {"_id": str(channel_id)},
        {"$set": {"last_message_id": message_id}},
        upsert=True,
    )
