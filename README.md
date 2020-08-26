## slackhab

Installs a python-based Slack bot which allows you to _chat_ to your openHAB server.

Requires an old-style bot which allows use of the Slack RTM API. New Slack apps don't support the RTM API.

#### Steps to run

1. Create a new Slack Real-Time Messaging Bot integration

2. Set the following env vars;
  - SLACKHAB_SLACK_TOKEN
  - SLACKHAB_SLACK_USER_ID
  - SLACKHAB_OPENHAB_URL
  - SLACKHAB_DEBUG

3. Run;
```
  docker run 
    -e "SLACKHAB_SLACK_TOKEN=xoxb-1234567890-12345678901234567890" 
    -e "SLACKHAB_SLACK_USER_UD=UXXXXXXX" 
    -e "SLACKHAB_OPENHAB_URL=http://openhab_ip:8080" 
    -e "SLACKHAB_DEBUG=DEBUG" 
    sumberboy12/slackhab
```

#### Example usage

Once connected you can issue commands such as;

```
# query state (supports partial matching)
items living

# update state (must match a single item)
update living_temp 23.45

# send commands (must match a single item)
send living_heater ON
```

