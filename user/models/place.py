# -*- coding: utf-8 -*-
import pymongo

from django.conf import settings


HOST = settings.MONGO_CONFIG["master"]["HOST"]
PORT = settings.MONGO_CONFIG["master"]["PORT"]
DB = settings.MONGO_CONFIG["master"]["DB"]
USERNAME = settings.MONGO_CONFIG["master"]["USERNAME"]
PASSWORD = settings.MONGO_CONFIG["master"]["PASSWORD"]


class Place(object):

    def __init__(self, lon, lat, user_id):
        self.lon = lon
        self.lat = lat
        self.user_id = user_id

    @classmethod
    def _get_cursor(cls):
        client = pymongo.MongoClient(HOST, PORT)
        db = client
        db.authenticate(USERNAME, PASSWORD, DB)
        return db

    @classmethod
    def get(cls, user_id):
        db = cls._get_cursor()
        obj = db.places.find_one({"user_id": user_id})
        if obj:
            place = Place(lon=obj["coordinates"][0],
                          lat=obj["coordinates"][1],
                          user_id=user_id)
            place.db = db
            return place
        return None

    @classmethod
    def add(cls, lon, lat, user_id):
        db = cls._get_cursor()
        data = {"coordinates": [lon, lat]}
        db.places.update({"user_id": user_id}, {"$set": data}, True)

    @classmethod
    def update(cls, user_id, data):
        db = cls._get_cursor()
        db.places.update({"user_id": user_id}, {"$set": data}, True)

    @classmethod
    def get_locations(cls, lon, lat, user_id, limit=20, skip=0):
        db = cls._get_cursor()
        objs = db.command(SON([("geoNear", "places"),
                               ("near", [float(lon), float(lat)]),
                               ("spherical", True),
                               ("distanceMultiplier", 6371)]))

        locations = []
        results = objs["results"]
        for result in results:
            location = {
                "lon": result["obj"]["coordinates"][0],
                "lat": result["obj"]["coordinates"][1],
                "dis": int(result["dis"]),
                "user_id": result["obj"]["user_id"]
            }
            locations.append(location)
        return locations

    def get_dis(self, to_user_id):
        obj = self.db.command(SON([("geoNear", "places"),
                                   ("near", [float(self.lon), float(self.lat)]),
                                   ("spherical", True),
                                   ("distanceMultiplier", 6371),
                                   ("query", {"user_id": int(to_user_id)})]))
        results = obj["results"]
        if results:
            dis = round(results[0]["dis"], 2)
            if dis < 0.01:
                dis = 0.01
            return dis
        return 0

    def get_multi_user_dis(self, user_ids, max_distance=None):
        command = [("geoNear", "places"),
                   ("near", [float(self.lon), float(self.lat)]),
                   ("spherical", True),
                   ("distanceMultiplier", 6371),
                   ("query", {"user_id": {"$in": user_ids}})]

        if max_distance:
            command.append(("maxDistance", max_distance))

        obj = self.db.command(SON(command))
        results = obj["results"]
        users_localtion = {}
        for result in results:
            dis = round(result["dis"], 2)
            if dis < 0.01:
                dis = 0.01
            user_id = result["obj"]["user_id"]
            users_localtion[user_id] = dis
        return users_localtion

    def get_near_user_dis(self):
        obj = self.db.command(SON([("geoNear", "places"),
                                   ("near", [float(self.lon), float(self.lat)]),
                                   ("spherical", True),
                                   ("distanceMultiplier", 6371),
                                   ("maxDistance", 100000),
                                   ("num", 100)]))
        results = obj["results"]
        users_localtion = {}
        for result in results:
            dis = round(result["dis"], 2)
            if dis < 0.01:
                dis = 0.01
            user_id = result["obj"]["user_id"]
            users_localtion[user_id] = dis
        return users_localtion
