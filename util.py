def indent(msg: str, indent=2):
    filler = ' ' * indent
    return filler + msg.replace('\n', '\n' + filler)
