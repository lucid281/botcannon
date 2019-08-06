#!/usr/bin/env bash

# Example script to demonstrate configuring a BotCannon bot with docker-compose
app_name="botcannon-demo"

plugin="jsonplaceholder"
plugin_config_key="${plugin}:url"

run_type="slack"
run_config="${run_type}:mybot"

COMPOSE_SERVICE='worker'  # container to use to run botcannon commands

# inject config commands into an interactive session and exit
# these commands can be used on botcannon deployed without docker.
echo "
### define the service...
./botcannon su service define ${app_name} ${plugin} ${plugin_config_key} ${run_type} ${run_config}

### add a parameter entry to satisfy entrypoint class
./botcannon su params add ${plugin_config_key}

### update kv data for parameter
./botcannon su params kv ${plugin_config_key} --base_url https://jsonplaceholder.typicode.com

### add parameter entry for slack
./botcannon su params add ${run_config}
" | docker-compose run ${COMPOSE_SERVICE} bash -i

docker-compose run ${COMPOSE_SERVICE} ./botcannon su params paste ${run_config} api_key
