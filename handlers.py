import json
import random
import re
from typing import Dict, Tuple

from fbchat import log

from models import Client, Handler, Message, Thread
from util import indent


class WakeWordHandler(Handler):
    wake_word_regex = r'^boto,? '
    handler: Handler

    def __init__(self, handler: Handler) -> None:
        self.handler = handler

    def name(self):
        return f'{type(self).__name__}({self.handler.name()})'

    def couldHandle(self, msg: Message):
        return (msg.text
                and re.match(self.wake_word_regex, msg.text, re.IGNORECASE)
                and self.handler.couldHandle(self._messageWithoutWakeword(msg)))

    def handle(self, msg: Message, client: Client):
        self.handler.handle(self._messageWithoutWakeword(msg), client)

    def _messageWithoutWakeword(self, msg: Message) -> Message:
        text_without_wake_word = re.sub(
            self.wake_word_regex, '', msg.text, flags=re.IGNORECASE)
        message = Message(text_without_wake_word,
                          msg.author_id, msg.author_name, msg.thread)
        return message


class HelpHandler(Handler):
    def couldHandle(self, msg: Message):
        return msg.textNorm().startswith('help')

    def handle(self, msg: Message, client: Client):
        client.sendText(
            msg.thread, 'Documentation at:\nhttps://github.com/DaemonF/boto/blob/master/README.md#commands')


class EchoHandler(Handler):
    def couldHandle(self, msg: Message):
        return msg.textNorm().startswith('echo')

    def handle(self, msg: Message, client: Client):
        client.sendText(msg.thread, msg.text.replace('echo', '', 1).strip())


class TellHandler(Handler):
    default_thread: Thread

    def __init__(self, default_thread: Thread) -> None:
        self.default_thread = default_thread

    def couldHandle(self, msg: Message):
        return msg.textNorm().startswith('tell')

    def handle(self, msg: Message, client: Client):
        text = msg.text.replace('tell', '', 1).strip()
        log.info(f'Telling defualt group:\n{indent(text)}')
        client.sendText(self.default_thread, text)
        client.sendText(msg.thread, 'Mischief managed.')


class ImageHandler(Handler):
    def couldHandle(self, msg: Message):
        return re.match(r'^(pug|kitteh|rocket|show .* the door)', msg.textNorm())

    def handle(self, msg: Message, client: Client):
        path = None
        if msg.textNorm().startswith('pug'):
            path = './pugs.txt'
        elif msg.textNorm().startswith('kitteh'):
            path = './kitteh.txt'
        elif msg.textNorm().startswith('rocket man'):
            path = './rocketmans.txt'
        elif msg.textNorm().startswith('rocket'):
            path = './rockets.txt'

        if path:
            count = 5 if "bomb" in msg.textNorm() else 1
            with open(path, 'r') as f:
                lines = f.readlines()
                random.shuffle(lines)
                for image_url in lines[:count]:
                    client.sendImage(msg.thread, image_url.strip())
            return

        show_the_door_match = re.match(
            r'show (.*) the door', msg.text, re.IGNORECASE)
        if show_the_door_match:
            name = show_the_door_match.group(1)
            client.sendText(msg.thread, f'Excuse me {name}, right this way...')
            client.sendImage(
                msg.thread, 'https://energy.gov/sites/prod/files/styles/borealis_photo_gallery_large_respondxl/public/door_5481543.jpg')
            return

        raise RuntimeError(f'Unknown image command.')


class PointsHandler(Handler):
    def couldHandle(self, msg: Message):
        return re.match(r'^(points|\+|-|forget about)', msg.textNorm())

    def handle(self, msg: Message, client: Client):
        if msg.textNorm().startswith('points'):
            points = self._loadPoints(msg.thread)
            if len(points) == 0:
                return client.sendText(msg.thread, 'No points.')
            text = ''
            for key, value in points.items():
                text += self._formatPoints(key, value) + '\n'
            return client.sendText(msg.thread, text)
        elif msg.textNorm().startswith('+'):
            increment, thing = self._parse(msg)
            if msg.author_name.strip().lower() in thing:
                return client.sendText(msg.thread, f"Fuck you, {msg.author_name}.")
            points = self._loadPoints(msg.thread)
            points[thing] = points.get(thing, 0) + increment
            self._storePoints(msg.thread, points)
            return client.sendText(msg.thread, self._formatPoints(thing, points[thing]))
        elif msg.textNorm().startswith('-'):
            increment, thing = self._parse(msg)
            points = self._loadPoints(msg.thread)
            points[thing] = points.get(thing, 0) - increment
            self._storePoints(msg.thread, points)
            return client.sendText(msg.thread, self._formatPoints(thing, points[thing]))
        elif msg.textNorm().startswith('forget about'):
            thing = msg.textNorm().replace('forget about', '', 1).strip()
            points = self._loadPoints(msg.thread)
            del points[thing]
            self._storePoints(msg.thread, points)
            return client.sendText(msg.thread, f'Huh? What\'s {thing}? I know nothing about {thing}.')
        else:
            raise RuntimeError(f'Unknown points command.')

    def _parse(self, msg: Message) -> Tuple[int, str]:
        match = re.match(r'[+-]([0-9]+) (.*)', msg.text)
        if not (match and len(match.groups()) == 2):
            raise RuntimeError(
                f'Bad format. Must be "+/-NUM SOME PHRASE"')
        increment = int(match.group(1))
        if increment <= 0:
            raise RuntimeError(f'Increment must be greater than 0.')
        thing = match.group(2).strip().lower()
        return increment, thing

    def _loadPoints(self, thread: Thread) -> Dict[str, int]:
        try:
            with open(f'./data/points-{thread.thread_id}.json', 'r') as f:
                return json.loads(f.read())
        except:
            return {}

    def _storePoints(self, thread: Thread, points: Dict[str, int]):
        with open(f'./data/points-{thread.thread_id}.json', 'w') as f:
            f.write(json.dumps(points))

    def _formatPoints(self, key: str, value: int):
        s = '' if value == 1 else 's'
        return f'{key[0].upper() + key[1:]} has {value} point{s}'


class SorryDaveHandler(Handler):
    def couldHandle(self, msg: Message):
        return True

    def handle(self, msg: Message, client: Client):
        client.sendText(
            msg.thread, f"I'm sorry {msg.author_name}, I can't do that.")


class Xkcd37Handler(Handler):
    def couldHandle(self, msg: Message):
        return re.search(r'([a-z]+)-(ass) ([a-z]+)', msg.text, re.IGNORECASE) and random.randint(0, 100) < 20

    def handle(self, msg: Message, client: Client):
        match = re.search(r'([a-z]+)-(ass) ([a-z]+)', msg.text, re.IGNORECASE)
        client.sendText(msg.thread,
                        f'Did you mean "{match.group(1)} {match.group(2)}-{match.group(3)}"?')
