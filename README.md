## slackhab

A python-based Slack bot which allows you to _chat_ to your openHAB server.

Requires an old-style Real-Time Messaging bot which permits use of the Slack RTM API. New Slack apps don't support the RTM API.

#### Steps to run

1. Create a new Slack RTM bot integration
  - Click [here](https://app.slack.com/apps-manage) and login to your Slack team
  - Click *Custom Integrations* -> *Bots* -> *Add to Slack*
  - Give your bot a name and click *Add bot integration*
  - Copy the *API Token* and use in `SLACKHAB_SLACK_TOKEN` below
  - Configure your bots name, description, icon, and add to any channels you wish to acces it from

2. You need to find the user id of your new bot. The easiest way to is run `slackhab` with `SLACKHAB_LOG_LEVEL=DEBUG`. When `slackhab` starts it will connect to Slack using your token and log some details about your bot, including the user id. Copy this into `SLACKHAB_SLACK_USER_UD` and restart.

3. Run via docker;
```
  docker run 
    -e "SLACKHAB_SLACK_TOKEN=xoxb-1234567890-12345678901234567890" 
    -e "SLACKHAB_SLACK_USER_UD=UXXXXXXX" 
    -e "SLACKHAB_OPENHAB_URL=http://openhab_ip:8080" 
    -e "SLACKHAB_LOG_LEVEL=DEBUG" 
    sumberboy12/slackhab
```

#### Supported commands

Once connected you can issue commands directly to `slackhab` via the *Apps* section in your Slack client (usually down the bottom under your direct messages).

| Command | Description | Example
| --------|-------------|--------
| `items <filter>` | Query the state of one or more items (filter optional) | `items gf_living`
| `update <item>` | Update the state of a single item | `update gf_living_temp 12.34`
| `send <item>` | Send command to a single item | `send GF_Living_Heater ON`

NOTE: all commands, filters and values are case insensitive. Partial item names can be used for `update` and `send` commands, as long as there is only a single match.
