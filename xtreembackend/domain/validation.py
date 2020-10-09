class Guard:

    @staticmethod
    def againstNone(value):
        if value == None:
            raise ValidationException()
        else:
            return value

    @staticmethod
    def access(dictionary, key):
        if isinstance(dictionary, dict) and key in dictionary:
            return dictionary[key]
        else:
            raise ValidationException()


class ValidationException(Exception):
    pass

def isListOf(l, predicate):
    return isinstance(l, list) and \
        all(map(predicate, l))

def isDictOf(x, isKeyType, isValueType):
    return isinstance(x, dict) and \
        all(map(isKeyType, x.keys())) and \
        all(map(isValueType, x.values()))
