class LiquidError(Exception):
    pass

class TagUnknown(LiquidError):
    pass

class TagAlreadyRegistered(LiquidError):
    pass

class EndTagUnexpected(LiquidError):
    pass