#!/usr/bin/python

import os
import json
import random
from fbchat import Client, log
from fbchat.models import *

random.seed()

def randomLineFrom(filename):
  with open(filename, 'r') as f:
    return random.choice(f.readlines()).strip()

def loadPoints(thread_id):
  try:
    with open(f'./data/points-{thread_id}.json', 'r') as f:
      return json.loads(f.read())
  except:
    return {}

def storePoints(points, thread_id):
  with open(f'./data/points-{thread_id}.json', 'w') as f:
    f.write(json.dumps(points))

def formatPoints(key, value):
  s = '' if value == 1 else 's'
  return f'{key[0].upper() + key[1:]} has {value} point{s}'

def indent(msg, indent=2):
  filler = ' ' * indent
  return filler + msg.replace('\n', '\n' + filler)

class Bot(Client):
  userCache = {}
  threadCache = {}

  def onInbox(self, **kwargs):
    pass

  def onMessageDelivered(self, **kwargs):
    pass

  def onMessageSeen(self, **kwargs):
    pass

  def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
    self.markAsDelivered(author_id, thread_id)
    self.markAsRead(author_id)

    def reply(message):
      log.info(f'Replying:\n{indent(message)}')
      self.send(Message(text=message), thread_id=thread_id, thread_type=thread_type)

    def replyImage(image_url):
      log.info(f'Replying with image:\n{indent(image_url)}')
      self.sendRemoteImage(image_url, thread_id=thread_id, thread_type=thread_type)

    if author_id != self.uid:
      try:
        text = message_object.text
        name = 'boto'
        if text.lower().startswith(f'{name} '):
          if author_id not in self.userCache:
            self.userCache[author_id] = self.fetchUserInfo(author_id)[author_id]
          author_name = self.userCache[author_id].first_name

          if thread_id not in self.threadCache:
            self.threadCache[thread_id] = self.fetchThreadInfo(thread_id)[thread_id]
          thread_name = self.threadCache[thread_id].name

          log.info(f'\n{author_name} in thread {thread_name} said:\n{indent(text)}')
          text = text[len(name) + 1:]

          if text.startswith('help'):
            return reply('Documentation at:\nhttps://github.com/DaemonF/boto/blob/master/README.md#commands')
          elif text.startswith('echo'):
            return reply(text.replace('echo ', ''))
          elif text.startswith('tell '):
            msg = text.replace('tell ', '')
            log.info(f'Telling defualt group:\n{indent(msg)}')
            return self.send(Message(text=msg), thread_id=os.environ['FB_DEFAULT_GROUP'], thread_type=ThreadType.GROUP)
          elif text.startswith('pug bomb'):
            for i in range(5):
              replyImage(randomLineFrom('./pugs.txt'))
            return
          elif text.startswith('pug me'):
            return replyImage(randomLineFrom('./pugs.txt'))
          elif text.startswith('kitteh bomb'):
            for i in range(5):
              replyImage(randomLineFrom('./kitteh.txt'))
            return
          elif text.startswith('kitteh'):
            return replyImage(randomLineFrom('./kitteh.txt'))
          elif text.startswith('rocket man'):
            return replyImage(randomLineFrom('./rocketmans.txt'))
          elif text.startswith('rocket'):
            return replyImage(randomLineFrom('./rockets.txt'))
          elif text.startswith('++'):
            thing = text.replace('++', '').strip().lower()
            if author_name.strip().lower() in thing:
              return reply(f"Fuck you, {author_name}.")
            points = loadPoints(thread_id)
            points[thing] = points.get(thing, 0) + 1
            storePoints(points, thread_id)
            return reply(formatPoints(thing, points[thing]))
          elif text.startswith('--'):
            thing = text.replace('--', '').strip().lower()
            points = loadPoints(thread_id)
            points[thing] = points.get(thing, 0) - 1
            storePoints(points, thread_id)
            return reply(formatPoints(thing, points[thing]))
          elif text.startswith('points'):
            points = loadPoints(thread_id)
            if len(points) == 0:
              return reply('No points.')
            msg = ''
            for key, value in points.items():
              msg += formatPoints(key, value) + '\n'
            return reply(msg)
          else:
            return reply('I\'m sorry Dave, I can\'t do that.')
      except:
        reply('X_X')
        raise

if __name__ == '__main__':
  client = Bot(os.environ['FB_USER'], os.environ['FB_PASS'])
  client.listen()
