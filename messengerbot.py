#!/usr/bin/python

import os
import json
import random
from fbchat import Client, log
from fbchat.models import *

class Bot(Client):
  def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
    self.markAsDelivered(author_id, thread_id)
    self.markAsRead(author_id)

    log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))

    if author_id != self.uid:
      to = thread_id
      type = thread_type
      text = message_object.text
      reply = None
      image_url = None
      if text.startswith('boto echo'):
        reply = text.replace('boto echo ', '')
      elif text.startswith('boto tell'):
        reply = text.replace('boto tell ', '')
        to = os.environ['FB_DEFAULT_GROUP']
        type = ThreadType.GROUP
      elif text.startswith('boto pug me'):
        with open('./pugs.txt', 'r') as f:
          image_url = random.choice(f.readlines()).strip()
      elif text.startswith('boto kitteh'):
        with open('./kitteh.txt', 'r') as f:
          image_url = random.choice(f.readlines()).strip()

      if image_url:
        self.sendRemoteImage(image_url, thread_id=to, thread_type=type)
      if reply:
        self.send(Message(text=reply), thread_id=to, thread_type=type)

if __name__ == "__main__":
  client = Bot(os.environ['FB_USER'], os.environ['FB_PASS'])
  client.listen()
