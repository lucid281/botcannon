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
        # base_url = 'https://jsonplaceholder.typicode.com'
        self.r = requests.Session()
        self.r.headers['Content-type'] = 'application/json'
        self.endpoints = {
            'posts': f'{base_url}/posts',
            'comments': f'{base_url}/comments',
            'albums': f'{base_url}/albums',
            'photos': f'{base_url}/photos',
            'todos': f'{base_url}/todos',
            'users': f'{base_url}/users',
        }

        self.users = Users(self)
        self._hidden = None


class Users:
    """
    Uses JsonTestBot to perform tasks with /users

    It's important to be mindful of the calls you make to a REST api as a chatbot.
    We could, unwisely get all users during __init__ but we don't don't need to for by_id.
    by_name is bad on purpose, we have could queried the api...
    ...but it was an opportunity to make a point...don't slow your bots down!!
    """
    def __init__(self, bot):
        self._b = bot

    def all(self):
        """Get all users by username as a dict"""
        return {i['username']: i for i in self._b.r.get(self._b.endpoints['users']).json()}

    def by_name(self, username):
        """Get a User object with username by getting all users"""
        users = self.all()
        if username in users:
            return User(users[username], self._b)
        else:
            return 'No user found.'

    def by_id(self, id):
        """Get a User object by id"""
        user_json = self._b.r.get(self._b.endpoints['users'], params=str(id)).json()[0]
        return User(user_json, self._b)


class User:
    """
    User inherits the keys values pairs from user_json as attributes.

    Then, using our instance of JsonTestBot (bot) we create methods dynamically
    from bot.endpoints that pertain to our User. In this case I saved myself from
    writing 4 additional methods for each category.

    Look for common ground!
    In this case the endpoint is the only thing that changes in the request. Ripe for meta.
    """
    def __init__(self, user_json, bot):
        # bot serves as session handling and app structure, the _ hides it from fire/torch
        self._b = bot

        # assign user_json fields as attrs to this class
        for attr in user_json:
            setattr(self, attr, user_json[attr])

        # assign methods with names from bot.endpoints to a generated function
        for endpoint in ["posts", "comments", "comments", "albums", "todos"]:
            # this is unique per iteration, create a new instance for the function
            url = self._b.endpoints[endpoint]

            # generate the function
            def get():
                # we are making the assumption that self.id exists from above.
                return self._b.r.get(url, params={'userId': self.id}).json()

            # set the method
            setattr(self, endpoint, get)  # < do not call () ! you want the function, not the result of the function


# _entrypoint_ is the name of the root class botcannon and will load using
# a modified version of fire that can be used to call this file directly (see below).
_entrypoint_ = 'JsonTestBot'

if __name__ == '__main__':
    import fire

    fire.Fire(JsonTestBot)
