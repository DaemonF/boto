#!/usr/bin/python

import re
import os
import json
import random
from fbchat import Client, log
from fbchat.models import *

random.seed()

def randomLineFrom(filename, count=1):
  with open(filename, 'r') as f:
    lines = f.readlines()
    if count == 1:
      return random.choice(lines).strip()
    elif count > 1:
      random.shuffle(lines)
      return map(lambda line: line.strip(), lines[:count])
    else:
      raise ValueError("count must be >= 1")

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
        wake_word_regex = r'^boto,? '
        if text and re.match(wake_word_regex, text, re.IGNORECASE):
          if author_id not in self.userCache:
            self.userCache[author_id] = self.fetchUserInfo(author_id)[author_id]
          author_name = self.userCache[author_id].first_name

          if thread_id not in self.threadCache:
            self.threadCache[thread_id] = self.fetchThreadInfo(thread_id)[thread_id]
          thread_name = self.threadCache[thread_id].name

          log.info(f'\n{author_name} in thread {thread_name} said:\n{indent(text)}')
          text = re.sub(wake_word_regex, '', text, flags=re.IGNORECASE)

          if text.startswith('help'):
            return reply('Documentation at:\nhttps://github.com/DaemonF/boto/blob/master/README.md#commands')
          elif text.startswith('echo'):
            return reply(text.replace('echo', '', 1).strip())
          elif text.startswith('tell'):
            msg = text.replace('tell', '', 1).strip()
            log.info(f'Telling defualt group:\n{indent(msg)}')
            self.send(Message(text=msg), thread_id=os.environ['FB_DEFAULT_GROUP'], thread_type=ThreadType.GROUP)
            return reply('Mischeif managed.')
          elif text.startswith('pug bomb'):
            for image_url in randomLineFrom('./pugs.txt', count=5):
              replyImage(image_url)
            return
          elif text.startswith('pug me'):
            return replyImage(randomLineFrom('./pugs.txt'))
          elif text.startswith('kitteh bomb'):
            for image_url in randomLineFrom('./kitteh.txt', count=5):
              replyImage(image_url)
            return
          elif text.startswith('kitteh'):
            return replyImage(randomLineFrom('./kitteh.txt'))
          elif text.startswith('rocket man'):
            return replyImage(randomLineFrom('./rocketmans.txt'))
          elif text.startswith('rocket'):
            return replyImage(randomLineFrom('./rockets.txt'))
          elif text.startswith('points'):
            points = loadPoints(thread_id)
            if len(points) == 0:
              return reply('No points.')
            msg = ''
            for key, value in points.items():
              msg += formatPoints(key, value) + '\n'
            return reply(msg)
          elif text.startswith('+'):
            match = re.match(r'\+([0-9]+) (.*)', text)
            if not (match and len(match.groups()) == 2):
              return reply(f'Bad format. Must be "{name} +NUM SOME PHRASE"')
            increment = int(match.group(1))
            if increment <= 0:
              return reply(f'Value must be greater than 0.')
            thing = match.group(2).strip().lower()
            if author_name.strip().lower() in thing:
              return reply(f"Fuck you, {author_name}.")
            points = loadPoints(thread_id)
            points[thing] = points.get(thing, 0) + increment
            storePoints(points, thread_id)
            return reply(formatPoints(thing, points[thing]))
          elif text.startswith('-'):
            match = re.match(r'\-([0-9]+) (.*)', text)
            if not (match and len(match.groups()) == 2):
              return reply(f'Bad format. Must be "{name} -NUM SOME PHRASE"')
            increment = int(match.group(1))
            if increment <= 0:
              return reply(f'Value must be greater than 0.')
            thing = match.group(2).strip().lower()
            points = loadPoints(thread_id)
            points[thing] = points.get(thing, 0) - increment
            storePoints(points, thread_id)
            return reply(formatPoints(thing, points[thing]))
          elif text.startswith('forget about'):
            thing = text.replace('forget about', '', 1).strip().lower()
            points = loadPoints(thread_id)
            del points[thing]
            storePoints(points, thread_id)
            return reply(f'Huh? What\'s {thing}? I know nothing about {thing}.')
          elif re.match(r'show (.*) the door', text.lower()):
             replyImage('https://energy.gov/sites/prod/files/styles/borealis_photo_gallery_large_respondxl/public/door_5481543.jpg')
             return reply('Excuse me sir, right this way.')
          else:
            return reply(f'I\'m sorry {author_name}, I can\'t do that.')
      except:
        reply('X_X')
        raise

if __name__ == '__main__':
  client = Bot(os.environ['FB_USER'], os.environ['FB_PASS'])
  client.listen()
