import os
import json
import uuid
from datetime import datetime

class MongoLikeCollection:
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.file_path = f"data/{collection_name}.json"
        
        # Ensure directory exists
        os.makedirs("data", exist_ok=True)
        
        # Initialize the collection file if it doesn't exist
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
    
    def _load_data(self):
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_data(self, data):
        with open(self.file_path, 'w') as f:
            json.dump(data, f, default=self._json_serial, indent=2)
    
    def _json_serial(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)
    
    def find(self, query=None):
        data = self._load_data()
        
        if not query:
            return data
        
        # Basic query support
        result = []
        for item in data:
            match = True
            for key, value in query.items():
                if key == '$or':
                    # Handle $or operator
                    or_match = False
                    for or_condition in value:
                        or_condition_match = True
                        for or_key, or_value in or_condition.items():
                            if or_key not in item or not self._match_value(item[or_key], or_value):
                                or_condition_match = False
                                break
                        if or_condition_match:
                            or_match = True
                            break
                    if not or_match:
                        match = False
                        break
                else:
                    # Handle direct key match
                    if key not in item or not self._match_value(item[key], value):
                        match = False
                        break
            
            if match:
                result.append(item)
        
        return result
    
    def _match_value(self, item_value, query_value):
        # Handle regex-like queries for strings
        if isinstance(query_value, dict) and '$regex' in query_value:
            pattern = query_value['$regex'].lower()
            options = query_value.get('$options', '')
            
            if 'i' in options and isinstance(item_value, str):
                return pattern in item_value.lower()
            elif isinstance(item_value, str):
                return pattern in item_value
            return False
        
        return item_value == query_value
    
    def find_one(self, query):
        result = self.find(query)
        return result[0] if result else None
    
    def insert_one(self, document):
        data = self._load_data()
        
        # Set _id if not provided
        if '_id' not in document:
            document['_id'] = str(uuid.uuid4())
        
        # Add the document
        data.append(document)
        self._save_data(data)
        
        class Result:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        
        return Result(document['_id'])
    
    def update_one(self, query, update):
        data = self._load_data()
        updated = False
        
        for i, item in enumerate(data):
            match = True
            for key, value in query.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            
            if match:
                # Handle $set operator
                if '$set' in update:
                    for key, value in update['$set'].items():
                        data[i][key] = value
                
                # Save changes
                self._save_data(data)
                updated = True
                break
        
        class Result:
            def __init__(self, modified_count):
                self.modified_count = modified_count
        
        return Result(1 if updated else 0)
    
    def delete_one(self, query):
        data = self._load_data()
        deleted = False
        
        for i, item in enumerate(data):
            match = True
            for key, value in query.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            
            if match:
                del data[i]
                self._save_data(data)
                deleted = True
                break
        
        class Result:
            def __init__(self, deleted_count):
                self.deleted_count = deleted_count
        
        return Result(1 if deleted else 0)
    
    def delete_many(self, query):
        data = self._load_data()
        original_length = len(data)
        
        # Filter out items that match the query
        new_data = []
        for item in data:
            match = True
            for key, value in query.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            
            if not match:
                new_data.append(item)
        
        # Save if items were removed
        if len(new_data) < original_length:
            self._save_data(new_data)
        
        class Result:
            def __init__(self, deleted_count):
                self.deleted_count = deleted_count
        
        return Result(original_length - len(new_data))
    
    def count_documents(self, query=None):
        return len(self.find(query))


class MongoLikeDB:
    def __init__(self):
        self.collections = {}
    
    def __getattr__(self, name):
        if name not in self.collections:
            self.collections[name] = MongoLikeCollection(name)
        return self.collections[name]


class MongoLike:
    def __init__(self):
        self.db = MongoLikeDB()

# Create global instance
mongo = MongoLike()