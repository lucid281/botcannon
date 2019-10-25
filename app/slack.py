import time
import json
import re

from slackclient import SlackClient
from slackclient.client import SlackNotConnected
from walrus.streams import Message

from botcannon.models import Collector


class SlackService(Collector):
    name = __name__

    def __init__(self, api_key):
        self.slack = SlackClient(api_key)
        self.status = self.slack.api_call("auth.test")
        if 'error' in self.status and 'invalid_auth' in self.status['error']:
            print(self.status)
            print('Unable to sign-in. Check API key.')
            exit(1)

        if not self.slack.rtm_connect(with_team_state=False, reconnect=True):
            print("Connection to Slack failed....")
            exit(1)

        if not self.slack.server:
            raise SlackNotConnected

    def read(self):
        json_data = self.slack.server.websocket_safe_read()
        if json_data != "":
            for d in json_data.split("\n"):
                msg = json.loads(d)
                msg['user_id'] = self.status['user_id']
                self.slack.process_changes(msg)
                for_user = self.validate(msg)
                if for_user:
                    yield for_user
        #         else:
        #             pass
        # else:
        #     yield



    @staticmethod
    def validate(slack_data):
        if not slack_data["type"] == "message":
            return None

        if "subtype" in slack_data:
            if "message_changed" not in slack_data['subtype']:
                return None
            message = slack_data['message']
            mention = re.search("^<@(|[WU].+?)>(.*)", slack_data['message']['text'])

        else:
            message = slack_data
            mention = re.search("^<@(|[WU].+?)>(.*)", message['text'])

        mentioned_user = mention.group(1) if mention else None
        input_cmd = mention.group(2).strip() if mention else None

        if mentioned_user != slack_data['user_id']:
            input_cmd = None

        if slack_data['channel'].startswith('D') and message['user'] != slack_data['user_id']:
            input_cmd = message['text']

        message['channel'] = slack_data['channel']
        message['as_user'] = True

        if 'thread_ts' in message:  # Reply to threads
            message['thread_ts'] = message['thread_ts']

        r = {i: json.dumps(message[i]) for i in message if i in ['channel', 'thread_ts', 'as_user']}
        return {**r, "text": input_cmd} if input_cmd else None

    def taskback(self, message: Message, **kwargs):
        # channel=channel, text=text, thread_ts=thread_ts, as_user=as_user)
        d = {i: json.loads(message.data[i]) for i in message.data if i not in ['text']}
        r = self.slack.api_call("chat.postMessage", **d, text=message.data['text'])
        return True if r else False
