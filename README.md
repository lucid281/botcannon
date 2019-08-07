# botcannon
transform plain python code into chatbots.

* things you DONT do with botcannon
  * write any connection handling code (just slack for now)
  * worry about input command logic
  
##### the botcannon way
botcannon takes python code like this:
```
import random

class Bot:
    rand = random.randint(0, 1000)

_entrypoint_ = "Bot" 
```
and makes a bot like this in slack:
```
User Name 13:37
  @mybot
```
```
mybot APP 13:37
  Type:        Bot
  String form: <bots.randobot.Bot object at 0x7f4848bb01d0>
  
  Usage:        
               rand
```
```
User Name:
  @mybot rand
```
```
mybot APP 13:37
  535
```

## about this repo
this repo is for the docker-compose component of botcannon and is to be used as a template for starting for your own bot ecosystem. it does however, contain the primary documentation for botcannon's usage. there is an example bot, `jsonplaceholder` that uses python requests included with the repo and documentation below.

botcannon's source (included as a submodule) is located here: https://github.com/lucid281/botcannon-source.

#### new repo from git clone
if you cloned this repo instead of using github's template feature, you have to rm git's db and  the botcannon submodule dir. then init and add botcannon as a submodule to your new custom repo:
```
[in cloned botcannon dir]
rm -rf .git
rm -rf dockerbuild/cannon/botcannon
git init
git submodule add git@github.com:lucid281/botcannon-source dockerbuild/cannon/botcannon
```
then to add your repo to your github:
https://help.github.com/en/articles/adding-an-existing-project-to-github-using-the-command-line


## dependencies
for docker: docker, docker-compose 

for bare metal: python 3.5+, and redis

any combination of docker and bare metal will work. 


### using docker-compose (preferred, fastest)
```bash
git clone --recursive git@github.com:lucid281/botcannon.git MYBOTS
cd MYBOTS
docker-compose build
```
where MYBOTS is your new repo dir name.


### using baremetal / hybrid
```bash
git clone --recursive git@github.com:lucid281/botcannon.git MYBOTS
cd MYBOTS
pip install --user dockerbuild/cannon/botcannon/requirements.txt
export PYTHONPATH=PATH_TO_REPO_DIR/botcannon:$PYTHONPATH
# assuming redis is up...
python -m botcannon
```
baremetal can be easier for dev or certain deployments. redis or botcannon processes can run on hardware or in docker. redis 5 is required (streams).

redis and botcannon talk with a shared socket writable by the current user in`/var/run/redis/redis-server.sock`, not tcp. the socket is in `sockets/`, see `docker-compose.yml`.

python has trouble loading botcannon from the `dockerbuild` path, so you can add the botcannon submodule to your path...
 ```
 export PYTHONPATH=PATH_TO_BOTCANNON-SOURCE_REPO/botcannon:$PYTHONPATH
 ```
... and `python -m botcannon` should work as the `./botcannon` script in the cannon container.

>botcannon is configured to run with `/run/redis/redis-server.sock`. if that is missing the cli will look to `sockets/redis-server.sock` in your PWD, allowing you to plug into the redis instance without a new container. useful for accessing multiple instances on the same host. 


# configure the demo
to run a botcannon bot, collectively called a service to botcannon, botcannon needs to know the following:
  * SERVICE_NAME - name the service.
  * PLUGIN - name of the python file (without .py) in `${PWD}/bot/`
  * ENTRY_CONFIG - config key for hashed key/value parameters to satisfy plugin's _entrypoint_.\_\_init__ parameters 
    * namespace here is global to the app and shared with RUN_CONFIG
  * RUN_TYPE - runner type, only `slack` for now. future data providers (irc, rocketchat, discord)
  * RUN_CONFIG - same as ENTRY_CONFIG but for the runner
    * namespace here is global to the app and shared with ENTRY_CONFIG

the `PLUGIN.py` file needs `_entrypoint_ = "SomeClass"` referencing the class botcannon will use as a root for the command tree.

read `configure.sh`.

`configure.sh`'s comments explain the config process, requirements and demo the usage at the same time. it is configured to add a service named `botcannon-demo` with `jsonplaceholder` as the plugin and slack as the 'runner'. all using `docker-compose`. `configure.sh` is crude in nature, but has a way to make api keys pasteable in the terminal and most importantly, a way to automate the config process.

#### starting botcannon runner/worker Manually
start `botcannon-demo`'s runner as configured (slack):
```
./botcannon run-runner botcannon-demo
```

start `botcannon-demo`'s worker as configured(jsonplaceholder):
```
./botcannon worker botcannon-demo
```
#### starting with docker-compose
```docker-compose up```
see `docker-compose.yml` for more (its just the commands above)


## explore botcannon-demo (jsonplaceholder bot)
now open slack, find the username for the bot/api_key you used. then send a junk DM to your bot to kick off the help. 

there is no capturing of std out just yet, so `print()` wont return to your bot.

happy hacking!

# botcannon usage
documentation reference's botcannon's execution generically. run commands in your desired environment according to notes below: 

#### cli commands on docker
if you are using docker, `./botcannon COMANND` can be run 2 ways.

1. `docker-compose run COMPOSE_SERVICE ./botcannon COMMAND` 
2. get a bash shell in a container with `docker-compose run COMPOSE_SERVICE bash -i`, then run `./botcannon COMANND`
where COMPOSE_SERVICE is the name the app in docker-compose.yml. (worker or runner will work)

and COMMAND is... well, the botcannon command you need to run.

#### cli commands on baremetal
baremetal installs will not have the `dockerbuild/cannon/botcannon-script` script as `./botcannon` in the project root, you can copy this to your project root or run `python -m botcannon` if you modified your PYTHONPATH to include botcannon.

## basic
run `./botcannon`in docker, or in your botcannon repo folder:
```
$ ./botcannon 
Type:        BotcannonCli
String form: <__main__.BotcannonCli object at 0x7fb1cbbc1bd0>
Docstring:   Welcome to botcannon!

Usage:       . 
             . bot
             . bots
             . help
             . ls
             . run-runner
             . runner
             . su
             . worker

```
each option maps to an attribute of `BOTCANNON_SOURCE_REPO_PATH/botcannon/__main__.BotcannonCli`

`fire` for python is the magic at work here. allowing you to call deeper and deeper into the objects returned by `botcannon`

try `bots`:
```
$ ./botcannon bots
jsonplaceholder: <class 'bot.jsonplaceholder.JsonTestBot'>
```
this is the all the plugins or 'bots' in `bots/` relative to your current path.
 
> `./botcannon bot`, the counterpart to `bots`, needs the name of a service definition we have not created just yet. a service definition is composed of the following pieces of data: a plugin name, plugin data, a runner name, and runner data.
 
if you're nosey, see the source for the 'bot' @ `bot/jsonplaceholder.py`, there are many useful comments there describing the bot. it is also a showcase for some of the thing that python and fire together let you do. not that you could before fire, but before fire it was hard to see what your code was doing. sorry for the pun.

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
this is manual access to the `_entrypoint_` defined in `jsonplaceholder.py`, (which is the `JsonTestBot` class), pointing botcannon in the right direction 

this command is good for testing some code locally, but you might end up putting api keys in your terminal. as you will learn botcannon is designed to handle this first pass of initialization for us. 

for now, lets play with direct entrypoint access via `bots`. take this command for example:
```
$ ./botcannon bots jsonplaceholder --base-url https://jsonplaceholder.typicode.com users by-id 2 posts 0
userId:    1
id:        1
title:     delectus aut autem
completed: false
```

`--base-url` was provided, satisfying the \_\_init__ parameters for the \_entrypoint_ defined in `jsonplaceholder.py`. 

now each addtional parameter on the command line brings us deeper:
  * `users` - JsonTestBot().users - train becomes Users object
  * `by-id`- JsonTestBot().users.by_id - Method of Users
  * `2` - JsonTestBot().users.by_id(2) - Call method with `2`, train becomes User object
  * `posts` - JsonTestBot().users.by_id(2).posts() - Call posts method of returned User object, train becomes list of dicts.
  * `0` - JsonTestBot().users.by_id(2).posts()[0] - Previous item a list, returning the first item with `0`, train becomes new dict

...and so on.

aside from the `--base-url`, this is exactly how you interact with the `jsonplaceholder` bot via slack as configured in the `botcannon-demo` service created by `configure.sh`.

# Todo

* improve docs
* clean up terminal output
* add more runners
* user management
