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

def extractOrThrow(result):
    if result.isOk():
        return result.extract()
    else:
        raise ValidationException(result.extract())

