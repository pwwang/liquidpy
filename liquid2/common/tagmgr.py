
from .exception import TagUnknown, TagAlreadyRegistered

TAGS = {}

def get_tag(tagname, tagargs):
    if tagname not in TAGS:
        raise TagUnknown(tagname)
    return TAGS[tagname](tagname, tagargs)

def register_tag(tagname, tag):
    # if tagname in TAGS:
    #     raise TagAlreadyRegistered(tagname)
    TAGS[tagname] = tag
