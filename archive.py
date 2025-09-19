import json
import copy
import os

# Activities
def _load_activities(file: str, images_dir: str) -> tuple[list[dict], dict[int, dict]]:
    """Load the activities in json format from the given filename"""
    with open("data" + os.sep + file, "r") as inf:
        activities = json.load(inf)

    activities.sort(key=lambda x: x["id"])
    for i, activity in enumerate(activities):
        activity["image"] = images_dir + activity["image"]

        if i > 0:
            activities[i-1]["next"] = activity["id"]
        if i + 1 < len(activities):
            activities[i+1]["prev"] = activity["id"]

    return activities, {activity["id"]: activity for activity in activities}

# This is a sort of cache to avoid opening a file or reading from the database
# Using getters with deepcopy allows adding values to the dictionaries without modifying the original data
_ACTIVITIES_CACHE = {
    None: _load_activities("activities_parsed.json", "/static/images/"), # Current year
    "23-24": _load_activities("activities_23-24.json", "/static/images_23-24/"),
}

def get_activities(year=None) -> list[dict]:
    """Returns a list of the activities sorted by id. Raises KeyError"""
    return copy.deepcopy(_ACTIVITIES_CACHE[year][0])

def get_activity(id: int, year=None) -> dict:
    """Get the information for one activity. Raises KeyError"""
    return copy.deepcopy(_ACTIVITIES_CACHE[year][1][id])
