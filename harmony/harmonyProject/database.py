from pymongo import MongoClient

class MongoDBConnection:
    def __init__(self):
        self.client = MongoClient('mongodb+srv://alvearMutis:TlsybI2hzLho9fZt@cluster0.zce1css.mongodb.net/?retryWrites=true&w=majority')
        self.db = self.client['HarmonyDB']
