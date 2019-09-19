"""
jsonplaceholder bot
=============================
TYPE: EXAMPLE
API: https://jsonplaceholder.typicode.com

The jsonplaceholder api is uniform enough that we can get away with
dynamically populating attrs/methods. This is a bit showy for an example,
but it demonstrates how dynamic a bot can be.

There is only 1 line of botcannon specific code, _entrypoint_ = 'JsonTestBot'

Currently stdout will not be returned to the user,
only the results of the attribute call chain from fire return to a bot.

"""
import requests
import json


class JsonTestBot:
    """
    --base-url https://jsonplaceholder.typicode.com

    The top of the command tree, all future classes depend on it
    When used by Botcannon, traversal begins here after satisfying __init__

    This simple class holds the session and some info for our future requests

    The base_url parameter is important

    Botcannon stores these parameters in redis, as defined for each service...
    ...this makes your bot code reusable for new bots with different api keys on the same host...
    ...a similar reuse happens with runners, allowing the same bot across many slacks.

    Each attribute is exposed as a command to the bot, but can be hidden from the user by prepending _
    """
    def __init__(self, base_url):
        base_url = 'https://app.rainforestqa.com/api/1'
        self.r = requests.Session()
        self.r.headers['Accept'] = 'application/json'
        self.r.headers['CLIENT_TOKEN'] = ''
        self.endpoints = {
            'runGroups': f'{base_url}/run_groups',
            'runs': f'{base_url}/runs',
            'runsInProgress': f'{base_url}/runs?state=in_progress'
        }

        self.runGroups = RunGroups(self)
        self.runs = Runs(self)
        self._hidden = None


class RunGroups:

    def __init__(self, bot):
        self._b = bot

    def all(self):
        """Get all run groups by title(group name) as a dict"""
        return {i["title"]: i for i in self._b.r.get(self._b.endpoints['runGroups']+"?page=1&page_size=100").json()}

    def names(self):
        result = []
        groups = self.all()
        for key in groups:
            item = groups[key]
            name = "(" + str(item["id"]) + ")  " + key
            result.append(name)
        return "\n".join(result)

    def by_id(self, group_id):
        groups = self.all()
        for key in groups:
            item = groups[key]
            if item["id"] == group_id:
                return key
        return "no id matched"

    def start(self, group_id):
        print("group id: ", group_id)
        """Get a Run Group object by id"""
        url = self._b.endpoints['runGroups']+"/"+str(group_id)+"/runs"
        group_key = self.by_id(group_id)
        if group_key == "no id matched":
            return "Group is invalid"

        payload = {"description": group_key}
        group_json = self._b.r.post(url, data=json.dumps(payload)).json()
        return "Started run group: " + group_json["description"]


class RunGroup:

    def __init__(self, group_json, bot):
        # bot serves as session handling and app structure, the _ hides it from fire/torch
        self._b = bot

        # assign group_json fields as attrs to this class
        for attr in group_json:
            setattr(self, attr, group_json[attr])

        # assign methods with names from bot.endpoints to a generated function
        for endpoint in ["runs"]:
            # this is unique per iteration, create a new instance for the function
            url = self._b.endpoints[endpoint]

            # generate the function
            def get():
                # we are making the assumption that self.id exists from above.
                return self._b.r.get(url, params={'run_group_id': self.id}).json()

            # set the method
            setattr(self, endpoint, get)  # < do not call () ! you want the function, not the result of the function


class Runs:
    def __init__(self, bot):
        self._b = bot

    def all(self):
        return {i['title']: i for i in self._b.r.get(self._b.endpoints['runs']).json()}

    def in_progress(self):
        return {i['description']: i for i in self._b.r.get(self._b.endpoints['runsInProgress']).json()}

    def status(self):
        in_progress_runs = self.in_progress()

        print("####in_progress: ", in_progress_runs)
        if not in_progress_runs:
            return "No running tests"

        result = []
        for key in in_progress_runs:
            item = in_progress_runs[key]
            progress = "(" + str(item["id"]) + ")  " + key + ":   " + str(item["current_progress"]["complete"]) + "/" + str(item["current_progress"]["total"]) + "  =>  " + str(item["current_progress"]["percent"]) + "%"
            result.append(progress)

        return "\n".join(result)

    def stop(self, run_id):
        result = self._b.r.delete(self._b.endpoints['runs']+"/"+str(run_id)).json()
        return "Aborted: " + result["description"]


class Run:
    def _init_(self, run_json, bot):
        self._b = bot

        for attr in run_json:
            setattr(self, attr, run_json[attr])

        for endpoint in ["runsInProgress"]:
            url = self._b.endpoints[endpoint]

            def get():
                return self._b.r.get(url, params={'run_id': self.id}).json()

            setattr(self, endpoint, get)


# _entrypoint_ is the name of the root class botcannon and will load using
# a modified version of fire that can be used to call this file directly (see below).
_entrypoint_ = 'JsonTestBot'

if __name__ == '__main__':
    import fire

    fire.Fire(JsonTestBot)
