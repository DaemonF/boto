#!/usr/bin/python3

import os
import json
import random
from typing import Dict, List

import fbchat
import fbchat.models
from fbchat import log

from handlers import (EchoHandler, HelpHandler, ImageHandler, PointsHandler,
                      SorryDaveHandler, TellHandler, WakeWordHandler, Xkcd37Handler)
from models import Client, Handler, Message, Thread
from util import indent

random.seed()


class Bot(fbchat.Client):
    userCache: Dict[int, fbchat.models.User] = {}
    threadCache: Dict[int, fbchat.models.Thread] = {}

    handlers: List[Handler] = []

    def onListening(self):
        default_group_id = int(os.environ['FB_DEFAULT_GROUP'])
        default_group = Thread(
            default_group_id, fbchat.models.ThreadType.GROUP, self.lookupThread(default_group_id))
        self.handlers = [
            WakeWordHandler(HelpHandler()),
            WakeWordHandler(EchoHandler()),
            WakeWordHandler(TellHandler(default_group)),
            WakeWordHandler(ImageHandler()),
            WakeWordHandler(PointsHandler()),
            # Must be last WakeWordHandler.
            WakeWordHandler(SorryDaveHandler()),
            Xkcd37Handler()
        ]
        fbchat.Client.onListening(self)

    def lookupUser(self, user_id: int) -> fbchat.models.User:
        if user_id not in self.userCache:
            self.userCache[user_id] = self.fetchUserInfo(user_id)[str(user_id)]
        return self.userCache[user_id]

    def lookupThread(self, thread_id: int) -> fbchat.models.Thread:
        if thread_id not in self.threadCache:
            self.threadCache[thread_id] = self.fetchThreadInfo(thread_id)[str(
                thread_id)]
        return self.threadCache[thread_id]

    def onInbox(self, **kwargs):
        pass

    def onMessageDelivered(self, **kwargs):
        pass

    def onMessageSeen(self, **kwargs):
        pass

    def onMarkedSeen(self, **kwargs):
        pass

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        if author_id != self.uid:
            self.markAsDelivered(author_id, thread_id)
            self.markAsRead(author_id)

            thread: Thread = Thread(
                thread_id, thread_type, self.lookupThread(thread_id).name)
            message: Message = Message(
                message_object.text, author_id, self.lookupUser(author_id).first_name, thread)
            client: Client = Client(self)

            try:
                log.info(
                    f'\n{message.author_name} in thread {thread.thread_name} said:\n{indent(message.text)}')
                for handler in self.handlers:
                    if (handler.couldHandle(message)):
                        try:
                            log.info(f'Using: {handler.name()}')
                            handler.handle(message, client)
                        except RuntimeError as e:
                            client.sendText(thread, f'Error: {e}')
                        break
            except:
                client.sendText(thread, 'X_X')
                raise


if __name__ == '__main__':
    client = Bot(os.environ['FB_USER'], os.environ['FB_PASS'])
    client.listen()
