
import fbchat
import fbchat.models
from fbchat import log

from util import indent


class Thread:
    thread_id: int
    thread_type: fbchat.models.ThreadType
    thread_name: str

    def __init__(self, thread_id: int, thread_type: fbchat.models.ThreadType, thread_name: str) -> None:
        self.thread_id = thread_id
        self.thread_type = thread_type
        self.thread_name = thread_name


class Client:
    client: fbchat.Client

    def __init__(self, client: fbchat.Client) -> None:
        self.client = client

    def sendText(self, to: Thread, text: str):
        log.info(f'Sending:\n{indent(text)}')
        self.client.send(fbchat.models.Message(text=text),
                         thread_id=to.thread_id, thread_type=to.thread_type)

    def sendImage(self, to: Thread, image_url: str):
        log.info(f'Sending image:\n{indent(image_url)}')
        try:
            self.client.sendRemoteImage(
                image_url, thread_id=to.thread_id, thread_type=to.thread_type)
        except fbchat.models.FBchatFacebookError:
            self.sendText(to, image_url)


class Message:
    text: str
    author_id: int
    author_name: str
    thread: Thread

    def __init__(self, text: str, author_id: int, author_name, thread) -> None:
        self.text = text or ""
        self.author_id = author_id
        self.author_name = author_name
        self.thread = thread

    def textNorm(self) -> str:
        """Retuns a normalized version of 'text' that has been lowercased and stripped."""
        return self.text.lower().strip()


class Handler:
    def name(self):
        return type(self).__name__

    def couldHandle(self, msg: Message) -> bool:
        raise NotImplementedError("Must override.")

    def handle(self, msg: Message, client: Client):
        raise NotImplementedError("Most override.")
