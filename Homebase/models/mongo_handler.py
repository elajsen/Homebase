from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo


class MongoHandler:
    def __init__(self):
        conn_str = "mongodb+srv://eliasmattson:Qtepa112@homebasedb.g2lna9o.mongodb.net/?retryWrites=true&w=majority"
        self.client = pymongo.MongoClient(conn_str)

        self.db_name = "Homebase"
        self.budget_history_collection = "budget_history"
        self.budget_current_week = "budget_current_week"

    def update_budget_history(self, history):
        try:
            self.insert_value(
                self.db_name, self.budget_history_collection, [history])
            print("Updated budget history")
        except Exception as e:
            print("Couldn't update budget history")
            print(e)

    def update_budget_current_week(self, history):
        try:
            self.insert_value(
                self.db_name, self.budget_current_week, [history])
            print("Updated budget history")
        except Exception as e:
            print("Couldn't update budget history")
            print(e)

    def structure_budget_history(self, budget_history):
        structured_history = []

        for key, value in budget_history[0].items():
            if key == "_id":
                continue
            value["week"] = key
            structured_history.append(value)
        return structured_history

    def get_budget_history(self):
        history = self.get_collection(
            self.db_name, self.budget_history_collection)
        return self.structure_budget_history(history)

    def get_budget_current_week(self):
        history = self.get_collection(
            self.db_name, self.budget_current_week)
        return self.structure_budget_history(history)

    def insert_value(self, db, collection, values):
        assert isinstance(values, list), "Values must be in list"
        assert isinstance(values[0], dict), "Items must be dict"
        try:
            self.client[db][collection].insert_many(values)
            print("Item inserted")
        except Exception as e:
            print("Couldn't insert item")
            print(str(e))

    def delete_values(self, db, collection, objects):
        assert len(objects) > 0, "Object ids list is empty..."

        try:
            self.client[db][collection].delete_many(objects)
            print(f"Deleted {len(objects)} items.")
        except Exception as e:
            print("Couldn't delete items...")
            print(f"{str(e)}")

    def get_collection(self, db, collection):
        res = self.client[db][collection].find()
        return res

    def search_collection(self, db, collection, filter):
        res = self.client[db][collection].find(filter)
        return res

    def list_databases(self):
        # Return the names of the databases
        for db in self.client.list_databases():
            print(db)

    def list_collections_in_db(self, db):
        # Return the names of collections in db
        for collection in self.client[db].collection_names():
            print(collection)

    def list_collections(self):
        # Return the names of all collections
        for db in self.client.list_databases():
            for collection in self.client[db.get("name")].collection_names():
                print(collection)

    def delete_database(self, db):
        try:
            self.client[db].drop()
            print(f"dropped db {db}")
        except Exception as e:
            print("Couldnt drop db")
            print(str(e))

    def delete_collection(self, db, collection):
        try:
            self.client[db].drop_collection(collection)
            print(f"Dropped collection {collection}")
        except Exception as e:
            print(f"Dropped collection {collection}")
            print(str(e))
