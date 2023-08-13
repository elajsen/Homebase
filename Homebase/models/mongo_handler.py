from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
from datetime import datetime
from django.conf import settings

import pandas as pd


class MongoHandler:
    def __init__(self):
        conn_str = settings.CREDENTIALS["mongo"]["username"]
        self.client = pymongo.MongoClient(conn_str)

        self.db_name = "Homebase"

        self.budget_history_collection = "budget_history"
        self.budget_current_week = "budget_current_week"
        self.budget_movements = "budget_movements"
        self.budget_icons = "budget_icons"

        self.bills = "bills"

    def mongo_return_to_df(self, dict):
        return pd.DataFrame.from_dict(dict)

    def update_budget_movements(self, movements):
        assert isinstance(
            movements, pd.DataFrame), f"type {type(movements)} should be pd.DataFrame"
        old_df = self.get_budget_movements()

        if "_id" in old_df.columns:
            old_df = old_df.drop(columns=["_id"])

        movements["date"] = movements["date"].astype(str)

        new_df = old_df.append(movements).drop_duplicates(subset=["id"])
        df_dict = new_df.to_dict("records")

        self.delete_collection(self.db_name, self.budget_movements)
        self.client[self.db_name][self.budget_movements]\
            .insert_many(df_dict)
        print("Updated budget movements")

    def update_budget_history(self, history):
        self.delete_collection(self.db_name, self.budget_history_collection)
        self.insert_value(
            self.db_name, self.budget_history_collection, history)
        print("Updated budget history")

    def update_budget_current_week(self, history):
        self.delete_collection(self.db_name, self.budget_current_week)
        self.insert_value(
            self.db_name, self.budget_current_week, [history])
        print("Updated budget history")

    def update_bills(self, new_bills):
        filter = {"_id": self.get_bills().get("_id")}
        update = {"$set": {}}

        for key in new_bills:
            update.get("$set")[key + "." + list(new_bills.get(key).keys())
                               [0]] = list(new_bills.get(key).values())[0]

        self.client[self.db_name][self.bills].update_one(filter, update)

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
        return list(history)

    def get_budget_current_week(self):
        history = self.get_collection(
            self.db_name, self.budget_current_week)
        return self.structure_budget_history(history)

    def get_budget_movements(self):
        movements = self.get_collection(
            self.db_name, self.budget_movements
        )
        df = self.mongo_return_to_df(movements)
        df["date"] = pd.to_datetime(df["date"])
        df = df.drop_duplicates(subset=["id"])

        return df

    def get_budget_icons(self):
        icons_dict = self.get_collection(
            self.db_name, self.budget_icons
        )
        return list(icons_dict)[0]

    def get_bills(self):
        icons_dict = self.get_collection(
            self.db_name, self.bills
        )
        return list(icons_dict)[0]

    def add_insertion_date(self, values):
        time = datetime.now().replace(microsecond=0)
        for val in values:
            val["data_time"] = str(time)
        return values

    def insert_value(self, db, collection, values):
        assert isinstance(values, list), "Values must be in list"
        assert isinstance(values[0], dict), "Items must be dict"

        values_with_date = self.add_insertion_date(values)

        try:
            self.client[db][collection].insert_many(values_with_date)
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
