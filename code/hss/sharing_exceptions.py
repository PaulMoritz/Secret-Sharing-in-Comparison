class ThresholdNotFulfilledException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class RequirementNotFulfilledException(IndexError):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class InvalidShareholderException(IndexError):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
