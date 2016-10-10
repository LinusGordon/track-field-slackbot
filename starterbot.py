import os
import time
import random
import re
from slackclient import SlackClient


# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXCUSE_COMMAND = "excuse"
greeting = ["hey guys", "hey", "hey boys", "hope everyones day is going well", "ayyy", "hello"]
inability = ["I can't come to practice today", "I can't run today", "wont be able to make it today", "wont be at practice", "cant come today", "unfortunately I can't come today"]
reason = ["I have an interview", "my parents are coming from out of town", "I have an essay due tomorrow", "I have a big test coming up", "this essay is ruining me", "I have a midterm", "I've got a lot of work", "my friend's visiting", "I'm not feeling well", "I'm sick", "I threw up earlier"]
goodbye = ["but I'll see you guys at lift tomorrow", "see you tomorrow", "have a good practice", "see you boys later"]

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):

    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "haha, nah" #a generic response if something goes wrong
    command = command.lower()
    command = re.sub('[!?,.]', '', command) # remove those
    if command.startswith('hey') or command.startswith('hi'):
        response = "hey watsup"
    if command.endswith('bot'):
        response = "no...of course I'm not a bot. I'm linus"
    if command.endswith(EXCUSE_COMMAND):
        response = random.choice(greeting) + ', ' + random.choice(inability) + ' because ' + random.choice(reason) + '. ' + random.choice(goodbye)
    slack_client.api_call("chat.postMessage", channel='#icantcometopractice',
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")