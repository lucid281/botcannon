# botcannon
=======================
this repo is for the docker-compose component of botcannon and is used for starting for your own bot ecosystem. it does
however, contain the primary documentation for botcannon. there is 1 example bot, `jsonplaceholder`, included
with the repo and documentation below.

botcannon's source (included as a submodule) is located here: https://github.com/lucid281/botcannon.


## Dependencies
Python 3.5+, docker, docker-compose and redis if bare metal.

#### Start with Docker-Compose (preferred, fastest)
```bash
git clone git@github.com:lucid281/botcannon.git MY_BOT_GROUP
cd MY_BOT_GROUP
git submodule update --init
docker-compose build
```
where MY_BOT_GROUP your new repo location.

next run `docker-compose up -d`, -d for daemon optionally (in the background). this will bring up only redis for now.

it's up to you to write the commands in your compose file to bring your bot(s) online with `up` later on.


#### Start with Baremetal / Hybrid (optional)
```bash
# CLONE LIKE ABOVE
pip install --user botcannon/botcannon/requirements.txt
export PYTHONPATH=PATH_TO_REPO_DIR/botcannon:$PYTHONPATH
# assuming redis is up...
python -m botcannon
```
baremetal can be easier for dev or certain deployments. redis or botcannon processes can run on hardware or in docker. redis 5 is required (streams).

redis and botcannon talk with a shared socket writable by the current user in`/var/run/redis/redis-server.sock`, not tcp. the socket is in `sockets/`, see `docker-compose.yml`.

python has trouble loading botcannon directly from this docker repo, so add the botcannon submodule to your path...
 ```
 export PYTHONPATH=PATH_TO_REPO_DIR/botcannon:$PYTHONPATH
 ```
... and `python -m botcannon` should work, functioning as the `./botcannon` script in your app container.

botcannon is configured to run with `/run/redis/redis-server.sock` by default. if that is missing the cli will look to `sockets/redis-server.sock` in your PWD, allowing you to pluginto the redis instance without a new container. 

### Configuring the Demo App
```
IMPORTANT NOTE:
If you are using DOCKER, `./botcannon COMANND` means `docker-compose run COMPOSE_SERVICE ./botcannon COMMAND".

Where COMPOSE_SERVICE is the name the app in docker-compose.yml. (worker or runner)

and COMMAND is... well, the botcannon command you need to run.

bare metal installs will not have the `dockerbuild/cannon/botcannon-script` script as `./botcannon` in the project root, you can copy this to your project root or run `python -m botcannon` if you modified your PYTHONPATH to include botcannon.
```

run `./botcannon bots` in your botcannon repo folder:
```
$ ./botcannon bots
jsonplaceholder: <class 'bot.jsonplaceholder.JsonTestBot'>
```
this is the all the plugins or 'bots' in `bots/` relative to your current path.
 
> `./botcannon bot` needs the name of a service definition (not yet created)-- the named record combined plugin name, plugin data, runner name, and runner data
 
see `jsonplaceholder.py` in `bot/`, there are many useful comments there. 

append `jsonplaceholder` to the previous `bots` command:
```
$ ./botcannon bots jsonplaceholder
Fire trace:
1. Initial component
2. Accessed property "bots" (/home/user/docker/botcannon/botcannon/botcannon/__main__.py:24)
3. Called routine "bots" (/home/user/docker/botcannon/botcannon/botcannon/__main__.py:24)
4. Accessed property "jsonplaceholder"
5. ('The function received no value for the required argument:', 'base_url')

Type:        type
String form: <class 'bots.jsonplaceholder.JsonTestBot'>
Docstring:   --base-url https://jsonplaceholder.typicode.com
[TRIMMED]
Usage:       . bots jsonplaceholder BASE_URL
             . bots jsonplaceholder --base-url BASE_URL
```
this is manual access to the `_entrypoint_` defined in `jsonplaceholder.py`, (which is `JsonTestBot`), pointing botcannon in the right direction 

this command is good for testing some code locally, but you might end up putting api keys in your terminal. 

lets just dive in. take this command for example:
```
$ ./botcannon bots jsonplaceholder --base-url https://jsonplaceholder.typicode.com users by-id 2 posts 0
userId:    1
id:        1
title:     delectus aut autem
completed: false
```

`--base-url` was provided, satisfying the \_\_init__ (not shown below). each parameter on the command line brings us deeper:
  * `users` - JsonTestBot().users - train becomes Users object
  * `by-id`- JsonTestBot().users.by_id - Method of Users
  * `2` - JsonTestBot().users.by_id(2) - Call method with `2`, train becomes User object
  * `posts` - JsonTestBot().users.by_id(2).posts() - Call posts method of returned User object, train becomes list of dicts.
  * `0` - JsonTestBot().users.by_id(2).posts()[0] - Previous item a list, returning the first item with `0`, train becomes new dict

...and so on.


### Configure a Bot
to actually run a botcannon bot, collectively called a service to botcannon, botcannon needs to know the following:
  * SERVICE_NAME - name or id of the service.
  * PLUGIN - name of the python file (without .py) in `${PWD}/bot/`
  * ENTRY_CONFIG - config key for hashed key/value parameters to satisfy plugin's _entrypoint_.\_\_init__ parameters 
  * RUN_TYPE - runner type, only slack for now. future providers (irc, rocketchat, discord)
  * RUN_CONFIG - same as ENTRY_CONFIG but for the runner

the plugin needs `_entrypoint_ = "SomeClass"` referencing the class botcannon will use as a root for the command tree.

read `configure.sh` for an example of how to configure a fresh bot, then run it to configure `botcannon-demo` in botcannon with slack.

#### Starting Botcannon Runner/Worker Manually
start the runner (slack):
```
./botcannon run-runner botcannon-demo
```

start the worker (jsonplaceholder):
```
./botcannon worker botcannon-demo
```
#### Starting Botcannon with docker-compose


## Use Botcannon-demo (jsonplaceholder bot)
now open slack, find the username for the bot/api_key you used. then send a junk DM to your bot to kick off the help. 

there is no capturing of std out just yet, so `print()` wont return to your bot. 

happy hacking!


###### Adding your repo to Github
since you cloned this repo, you have to clear out git and the submodule dir, then init and re-add the submodule to add your custom build to git:
```
[in cloned botcannon dir]
rm -rf .git
rm -rf botcannon
git init
git submodule add git@github.com:Etison/botcannon-code dockerbuild/cannon/botcannon/botcannon
```
Now follow: 
https://help.github.com/en/articles/adding-an-existing-project-to-github-using-the-command-line

# Todo

* improve docs
* clean up terminal output
* add more runners
* user management
