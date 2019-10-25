from MeteorClient import MeteorClient
import time
import json
from walrus import Message

from botcannon.models import Collector


class RocketChatBot(Collector):
    def __init__(self, user, password, server):
        self.username = user
        self.password = password
        self.server = server
        self.debug = True

        self._prefixs = []

        self.client = client = MeteorClient(server)

        # registering internal handlers (callbacks)
        self.client.on('logging_in', self._logging_in)
        self.client.on('connected', self._connected)
        self.client.on('closed', self._closed)
        self.client.on('failed', self._failed)
        self.client.on('added', self._added)
        self.client.on('changed', self._changed)
        self.client.on('unsubscribed', self._unsubscribed)
        self.client.on('subscribed', self._subscribed)
        self.messages = []

    """
    Internal events handlers

    When an even as defined above is triggered, these will run.
    """

    def _logging_in(self):
        print('[+] rocketchat: logging in')

    def _connected(self):
        print("[+] rocketchat: connected")
        # self.client.subscribe('stream-room-messages', [], self.cb1)

    def _closed(self, code, reason):
        print('[-] rocketchat: connection closed: %s (%d)' % (reason, code))

    def _failed(self, collection, data):
        print('[-] %s' % str(data))

    def _added(self, collection, id, fields):
        print('[+] %s: %s' % (collection, id))

        if not fields.get('args'):
            return

        args = fields['args']

        if args[0] == "GENERAL":
            print("[+] message: general, skipping")
            return

        if args[1].get('msg'):
            return self._incoming(args[1])

        if args[1].get('attachments'):
            return self._downloading(args[1])

        print(args)
        print(args[0])
        print(args[1])

        # for key, value in fields.items():
        #    print('[+]  %s: %s' % (key, value))

    def _changed(self, collection, id, fields, cleared):

        print('[+] changed: %s %s' % (collection, id))

        for key, value in fields.items():
            print('[+]  field %s: %s' % (key, value))

        for key, value in cleared.items():
            print('[+]  cleared %s: %s' % (key, value))

        if 'args' in fields:
            self.messages.append(fields)

    def _unsubscribed(self, subscription):
        print('[+] unsubscribed: %s' % subscription)

    def _subscribed(self, subscription):
        print('[+] subscribed: %s' % subscription)

    """
    Internal callback handlers
    """

    def cb_login(self, error, data):
        if not error:
            if 'id' in data:
                self.current_user = data['id']

            return

        print('[-] callback error:')
        print(error)

    def cb_messages(self, data):
        if data:
            self.messages.append(data)

        if not self.debug:
            return

        else:
            print("[+] callback success")

    """
    Internal dispatcher
    """

    def _incoming(self, data):
        print("[+] Message from %s: %s" % (data['u']['username'], data['msg']))

        for prefix in self._prefixs:
            if data['msg'].startswith(prefix['prefix']):
                prefix['handler'](self, data)

    def _downloading(self, data):
        print("[+] attachement from %s: %d files" % (data['u']['username'], len(data['attachments'])))

    """
    Public initializers
    """

    def addPrefixHandler(self, prefix, handler):
        self._prefixs.append({'prefix': prefix, 'handler': handler})

    def read(self):
        self.client.connect()
        time.sleep(0.1)
        self.client.login(self.username, self.password.encode('utf-8'), callback=self.cb_login)
        time.sleep(0.1)
        self.client.subscribe('stream-room-messages', ['__my_messages__', True], self.cb_messages)
        time.sleep(0.1)

        while True:
            try:
                m = self.messages.pop()
                if 'args' not in m:
                    continue
                message, room = m['args']
                if 'msg' in message and 'u' in message:
                    if message['u']['username'] != self.username and room['roomType'] == 'd':
                        r = {'msg': message['msg'], 'rid': message['rid']}
                        yield r
            except KeyboardInterrupt:
                break
            except IndexError:
                yield

    def taskback(self, message: Message):
        if 'text' in message.data and 'rid' in message.data:
            rid = message.data['rid']
            send = {'msg': message.data['text'], 'rid': rid}
            self.client.call('sendMessage', [send], None)
