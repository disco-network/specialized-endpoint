from .validation import ValidationException

# ======
# Utility definitions
# Data types: see below
# ======

class Result:
    @staticmethod
    def success(value):
        return Result(True, value)

    @staticmethod
    def fail(error):
        return Result(False, error)

    @staticmethod
    def ensure(requirements):
        def processRequirement(r):
            (cond, error) = r
            return None if cond else error
        errors = [x for x in map(processRequirement, requirements) if x is not None]
        if len(errors) == 0:
            return Result.success(None)
        else:
            return Result.fail(errors)

    def __init__(self, ok, value):
        self.ok = ok
        self.value = value

    def isOk(self):
        return self.ok

    def extract(self):
        return self.value

    def map(self, f):
        if self.isOk():
            return Result.success(f(self.extract()))
        else:
            return self

class Maybe:
    @staticmethod
    def value(value):
        return Maybe(True, value)

    @staticmethod
    def nothing():
        return Maybe(False)

    def __init__(self, hasValue, value=None):
        self._hasValue = hasValue
        self._value = value

    def hasValue(self):
        return self._hasValue

    def extract(self):
        return self._value

# ======
# Here come the data types
# ======

class Nullable:
    def __init__(self, innerType):
        self.innerType = innerType

    def equals(self, otherType):
        return isinstance(otherType, Nullable) and self.innerType.equals(otherType.innerType)

    def serialize(self, data):
        if not data.hasValue():
            return None
        else:
            return self.innerType.serialize(data.extract())

    def create(self, data):
        if data is None:
            return Maybe.nothing()
        else:
            innerObject = self.innerType.create(data)
            return Maybe.value(innerObject)

class AggregateDataType:
    def __init__(self, schema, consistencyCheck):
        self.schema = schema
        self.consistencyCheck = consistencyCheck

    def getSchema(self):
        return self.schema

    def equals(self, otherType):
        return self == otherType

    def serialize(self, fields):
        data = {}
        for (field, fieldType) in self.getSchema().items():
            data[field] = fieldType.serialize(fields[field])

        return data

    # might throw a ValidationException
    def create(self, data):
        self.checkPrerequisites(data)
        fields = self.parseFields(data)

        result = self.consistencyCheck(fields)
        if not result.isOk():
            raise ValidationException({
                "message": "AggregateDataType: consistency check failed",
                "innerErrors": result.extract(),
            })

        return fields

    def checkPrerequisites(self, data):
        if not isinstance(data, dict):
            raise ValidationException("AggregateDataType: data must be a dictionary")

        for (field, fieldType) in self.schema.items():
            if field not in data:
                raise ValidationException("AggregateDataType: field " + field + " is missing")

    def parseFields(self, data):
        fields = {}
        errors = {}
        errorsOccured = False

        for (field, fieldType) in self.schema.items():
            try:
                fields[field] = fieldType.create(data[field])
            except ValidationException as e:
                errorsOccured = True
                errors[field] = e

        if errorsOccured:
            errorObject = {
                "message": "AggregateDataType: could not parse fields",
                "innerErrors": errors
            }
            raise ValidationException(errorObject)
        else:
            return fields

class IntDataType:
    @staticmethod
    def equals(otherType):
        return otherType == IntDataType

    @staticmethod
    def serialize(value):
        return value

    @staticmethod
    def create(data):
        if isinstance(data, int):
            return data
        else:
            raise ValidationException("should be an integer")

class StringDataType:
    @staticmethod
    def equals(otherType):
        return otherType == StringDataType

    @staticmethod
    def serialize(value):
        return value

    @staticmethod
    def create(data):
        if isinstance(data, str):
            return data
        else:
            raise ValidationException("should be a string")

class ListDataType:
    def __init__(self, innerType):
        self.innerType = innerType

    def equals(self, otherType):
        return isinstance(otherType, ListDataType) and self.innerType.equals(otherType.innerType)

    def serialize(self, items):
        return list(map(lambda item: self.innerType.serialize(item), items))

    def create(self, data):
        if isinstance(data, list):
            try:
                return list(map(lambda inner: self.innerType.create(inner), data))
            except ValidationException as e:
                # This implementation only reports the first error while parsing the list.
                # It would be possible to write a more sophisticated method that
                # reports errors for all items.
                raise ValidationException({
                    "message": "ListDataType: could not parse items",
                    "innerErrors": e,
                })
        else:
            raise ValidationException({
                "message": "ListDataType: should be a list"
            })

class EnumDataType:
    def __init__(self, options):
        self.options = options

    def equals(self, otherType):
        return self == otherType

    def serialize(self, value):
        return value

    def create(self, data):
        if data in self.options:
            return data
        else:
            raise ValidationException("EnumDataType: invalid value")

class MapDataType:
    def __init__(self, keyType, valueType):
        if keyType not in [IntDataType, StringDataType]:
            raise Exception("illegal key type")
        self.keyType = keyType
        self.valueType = valueType

    def equals(self, otherType):
        return isinstance(otherType, MapDataType) and \
            self.keyType.equals(otherType.keyType) and \
            self.valueType.equals(otherType.valueType)

    def serialize(self, data):
        serialized = {}
        for (key, value) in data.items():
            serialized[self.keyType.serialize(key)] = self.valueType.serialize(value)
        return serialized

    def create(self, data):
        if isinstance(data, dict):
            obj = {}
            for (key, value) in data.items():
                try:
                    keyResult = self.keyType.create(key)
                except ValidationException as e:
                    raise ValidationException({
                        "message": "MapDataType: could not parse key " + key,
                        "innerErrors": e
                    })
                try:
                    valueResult = self.valueType.create(value)
                except ValidationException as e:
                    raise ValidationException({
                        "message": "MapDataType: could not parse value for " + key,
                        "innerErrors": e
                    })
                
                obj[keyResult] = valueResult
            return obj
        raise ValidationException("should be a dictionary")
