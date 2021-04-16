#
# Copyright (c) 2020 by Philipp Scheer. All Rights Reserved.
#

import time
from jarvis import Database, Security
from .Slot import Slot
from .Intent import Intent
from .User import User
from functools import wraps


def benchmark(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        if end-start > 1:
            print(f"Skill::{func.__name__} took {end-start}s")
        return res
    return wrap


class Skill:
    @benchmark
    def __init__(self, id: str = None, new: bool = False, existing_data: dict = None) -> None:
        self._unused_intent = None
        if id is None and existing_data is None:
            new = True
        if new:
            self.skill = {
                "created-at": int(time.time()),
                "modified-at": int(time.time()),
                "name": "New Skill",
                "icon": {
                    "icon": None,
                    "color": None
                },
                "social": {
                    "likes": [],
                    "comments": [],
                    "downloads": [],
                    "rating": 3.5
                },
                "intents": [],
                "quality": 0,
                "language": None,
                "description": None,
                "public": False,
                "id": Security.id(64)   # TODO: check that this id doesn't exist already!
            }
        elif existing_data is not None:
            self.skill = existing_data
        else:
            result = Database().table("skills").find({"id": id})
            if result.found:
                self.skill = result[0]
                self._update_intents()
                self._update_rating()
                self._update_quality()
            else:
                self.skill = None
        self.new = new


    # OBJECT FUNCTIONS
    def __getitem__(self, key) -> any:
        return self.skill[key]

    def __setitem__(self, key, value) -> None:
        self.skill[key] = value

    def __dict__(self) -> str:
        self._reverse_intents()
        return self.skill


    # PROPERTIES
    @property
    def found(self):
        return self.skill is not None

    @staticmethod
    def all(as_json: bool = False, resolve_slots: bool = False):
        skills = list(Database().table("skills").all())
        for i in range(len(skills)):
            if as_json:
                del skills[i]["_rev"]
                del skills[i]["_id"]
                skills[i] = Skill(existing_data=skills[i]).__dict__()
            else:
                skills[i] = Skill(existing_data=skills[i])
            
            if resolve_slots:
                for j in range(len(skills[i]["intents"])):
                    for slot_name in skills[i]["intents"][j]["slots"]:
                        skills[i]["intents"][j]["slots"][slot_name] = Slot(skills[i]["intents"][j]["slots"][slot_name]).__dict__()
                        del skills[i]["intents"][j]["slots"][slot_name]["_rev"]
                        del skills[i]["intents"][j]["slots"][slot_name]["_id"]
        return skills


    # INTENT ACTIONS
    @benchmark
    def add_intent(self, intent: Intent):
        self.skill["intents"].append(intent.__dict__())

    @benchmark
    def update_intent(self, intent_id: str, new_intent: Intent) -> bool:
        successful_insert = False
        for i in range(len(self.skill["intents"])):
            intent = self.skill["intents"][i]
            if intent["id"] == intent_id:
                self.skill["intents"][i] = new_intent.__dict__()
                successful_insert = True
        if not successful_insert and self._unused_intent:
            if intent_id == self._unused_intent["id"]:
                self.add_intent(new_intent)
        return successful_insert

    @benchmark
    def get_intent(self, id: str) -> Intent:
        for intent in self.skill["intents"]:
            if intent["id"] == id:
                return Intent(False, intent)
        if self._unused_intent and self._unused_intent["id"] == id:
            return Intent(False, self._unused_intent)
        return None

    @benchmark
    def remove_intent(self, id_or_intent: any) -> Intent:
        if isinstance(id_or_intent, Intent):
            pass
        elif isinstance(id_or_intent, str):
            id_or_intent = self.get_intent(id_or_intent)
            if not id_or_intent:
                return False
        else:
            return False
        new_intents = []
        for intent in self.skill["intents"]:
            if intent["id"] != id_or_intent["id"]:
                new_intents.append(intent)
        self.skill["intents"] = new_intents
        self.save()
        return True

    @benchmark
    def unused_intent(self) -> dict:
        return self._unused_intent


    # DATABASE ACTIONS
    @benchmark
    def save(self):
        self._reverse_intents()
        self.skill["modified-at"] = int(time.time())
        Database().table("skills").insert(self.skill)

    @benchmark
    def delete(self):
        Database().table("skills").find({"id": self.skill["id"]}).delete()


    # INTERNAL ACTIONS
    @benchmark
    def _update_rating(self) -> None:
        rating = [3.5]
        weights = [1]
        for comment in self.skill["social"]["comments"]:
            rating.append(comment["rating"])
            weight = 1
            
            days_diff = (time.time() - comment["modified-at"]) / 60 / 60 / 24
            if days_diff > 365:
                weight -= 0.5
            elif days_diff > 365/2:
                weight -= 0.25
            elif days_diff > 60:
                weight -= 0.1

            message_length = len(comment["message"])
            if message_length < 10:
                weight -= 0.25
            if message_length < 50:
                weight -= 0.1
            if message_length > 100:
                weight += 0.2
            if message_length > 200:
                weight += 0.35

            weights.append(weight)

        final_rating = sum(rating[g] * weights[g] for g in range(len(rating))) / sum(weights)
        self.skill["social"]["rating"] = final_rating

    @benchmark
    def _update_quality(self) -> None:
        intent_quality = 0
        for intent in self.skill["intents"]:
            intent_quality += intent["quality"]
        try:
            final_quality = intent_quality / len(self.skill["intents"])
        except ZeroDivisionError:
            final_quality = 0
        self.skill["quality"] = final_quality

    @benchmark
    def _update_intents(self) -> None:
        new_intent_array = []
        for intent in self.skill["intents"]:
            if intent["created-at"] == intent["modified-at"]: # not modified yet
                self._unused_intent = Intent(False, intent)
            else:
                new_intent_array.append(Intent(False, intent))
        self.skill["intents"] = new_intent_array

    @benchmark
    def _reverse_intents(self) -> None:
        for i in range(len(self.skill["intents"])):
            intent = self.skill["intents"][i]
            if isinstance(intent, Intent):
                self.skill["intents"][i] = intent.__dict__()
