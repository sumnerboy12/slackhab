import logging
import os
import requests
import json

# pip install slackclient (python 3.6+)
from slack import RTMClient

# initialise logging (default to INFO)
logging.basicConfig(level=os.getenv("SLACKHAB_DEBUG", "INFO"))

# retrieve our env vars
SLACK_TOKEN = os.getenv("SLACKHAB_SLACK_TOKEN", None)
SLACK_USER_ID = os.getenv("SLACKHAB_SLACK_USER_ID", None)
OPENHAB_URL = os.getenv("SLACKHAB_OPENHAB_URL", None)

# headers required for openhab REST API requests
HEADERS = { 'Content-Type': 'text/plain' }

def check_response(web_client, channel, r):
    # check our rest api call was successful
    if r.status_code < 400:
        return True

    # log the response code/reason back to our slack channel
    web_client.chat_postMessage(channel=channel, text="```%d: %s```" % (r.status_code, r.reason))
    return False

def get_items(web_client, channel, filter):
    # cache this maybe?
    url = OPENHAB_URL + '/rest/items'
    r = requests.get(url, headers=HEADERS)

    if not check_response(web_client, channel, r):
        return []

    if filter is not None:
        filter = filter.lower()

    items = []

    for item in json.loads(r.content):
        name = item['name'].lower()
        if filter is None or filter in name:
            items.append(item)

    return items

def get_single_item(web_client, channel, filter):
    items = get_items(web_client, channel, filter)
    items_count = len(items)

    if items_count == 0:
        web_client.chat_postMessage(channel=channel, text="```No item found matching '%s'```" % (filter))
        return None

    if items_count == 1:
        logging.debug("Found single matching item: %s" % (items[0]['name']))
        return items[0]

    # check if we have an exact match
    for item in items:
        name = item['name']
        if name.lower() == filter.lower():
            logging.debug("Found multiple matching items but one was an exact match: %s" % (name))
            return item

    web_client.chat_postMessage(channel=channel, text="```Found %d items matching '%s', please restrict your filter```" % (items_count, filter))
    web_client.chat_postMessage(channel=channel, text="```%s```" % (dump_items(items)))
    return None

def dump_items(items):
    output = ""
    maxtypelen = 0
    maxnamelen = 0

    # get the max name and type lengths so we can format our output nicely
    for item in items:
        name  = item['name']
        type  = item['type']
        if len(type) > maxtypelen:
            maxtypelen = len(type)
        if len(name) > maxnamelen:
            maxnamelen = len(name)

    for item in items:
        name  = item['name']
        state = item['state']
        type  = item['type']
        output = output + "%s%s%s\n" % ( type.ljust( maxtypelen + 5 ), name.ljust( maxnamelen + 5 ), state )
        if len(output) >= 3000:
            output = output + "... (too much output, please specify a filter)"
            break

    return output

def normalise_value(state):
    if state.lower() == "on":
        return "ON"
    if state.lower() == "off":
        return "OFF"
    if state.lower() == "open":
        return "OPEN"
    if state.lower() == "closed":
        return "CLOSED"

    return state

def get_command_text(channel, user, text):
    if channel == "" or channel is None:
        return None
    if user == "" or user is None:
        return None
    if text == "" or text is None:
        return None

    # check for a message directed at our bot
    user_tag = "<@%s>:" % (SLACK_USER_ID)
    if text.startswith(user_tag):
        return text[len(user_tag):]

    # check for a DM to our bot
    if channel.startswith("D"):
        return text

    return None

@RTMClient.run_on(event="message")
def handle_message(**payload):
    data = payload['data']
    web_client = payload['web_client']

    # what did we receive?
    logging.debug("Incoming message: %s" % (str(data)))

    # check we have sufficient details
    if 'channel' not in data or 'user' not in data or 'text' not in data:
        return

    channel = data['channel']
    user = data['user']
    text = data['text']

    # first check if we are interested in this command
    command_text = get_command_text(channel, user, text)

    if command_text is None:
        return

    tokens = command_text.split()
    if len(tokens) == 0:
        return

    command = tokens[0].lower()
    logging.debug("Command: %s" % (command))

    if command == "send" and len(tokens) >= 3:
        filter = tokens[1]
        value = " ".join(tokens[2:])

        item = get_single_item(web_client, channel, filter)
        if item is None:
            return

        url = OPENHAB_URL + '/rest/items/' + item['name']
        r = requests.post(url, headers=HEADERS, data=normalise_value(value))

        if check_response(web_client, channel, r):
            web_client.chat_postMessage(channel=channel, text="```Sent %s command to %s```" % (value, item['name']))

    elif command == "update" and len(tokens) >= 3:
        filter = tokens[1]
        value = " ".join(tokens[2:])

        item = get_single_item(web_client, channel, filter)
        if item is None:
            return

        url = OPENHAB_URL + '/rest/items/' + item['name'] + '/state'
        r = requests.put(url, headers=HEADERS, data=normalise_value(value))

        if check_response(web_client, channel, r):
            web_client.chat_postMessage(channel=channel, text="```Sent %s update to %s```" % (value, item['name']))

    elif command == "status" and len(tokens) >= 2:
        filter = tokens[1]

        item = get_single_item(web_client, channel, filter)
        if item is None:
            return

        url = OPENHAB_URL + '/rest/items/' + item['name'] + '/state'
        r = requests.get(url, headers=HEADERS)

        if check_response(web_client, channel, r):
            web_client.chat_postMessage(channel=channel, text="```%s is %s```" % (item['name'], r.text))

    elif command == "items":
        filter = None
        if len(tokens) > 1:
            filter = tokens[1]

        items = get_items(web_client, channel, filter)
        logging.debug("%d items match %s" % (len(items), filter))

        if len(items) == 0:
            if filter is None:
                web_client.chat_postMessage(channel=channel, text="```No items found```")
            else:
                web_client.chat_postMessage(channel=channel, text="```No items found matching '%s'```" % (filter))
        else:
            web_client.chat_postMessage(channel=channel, text="```%s```" % (dump_items(items)))

logging.info("Starting Slack RTM client...")
rtm_client = RTMClient(token=SLACK_TOKEN)
rtm_client.start()
