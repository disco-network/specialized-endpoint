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

    def nothing():
        return Maybe(False)

    def __init(self, hasValue, value=None):
        self._hasValue = hasValue
        self.value = value

    def hasValue(self):
        return self._hasValue

    def extract(self):
        return self.value

class Nullable:
    def __init__(self, innerType):
        self.innerType = innerType

    def equals(self, otherType):
        return isinstance(otherType, Nullable) and self.innerType.equals(otherType.innerType)

    def serialize(self, data):
        if not data.hasValue():
            return None
        else:
            return self.innerType.serialize(value.extract())

    def create(self, data):
        if data is None:
            return Result.success(Maybe.nothing())
        else:
            return self.innerType.create(value).map(lambda x: Maybe.value(x))

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

    def create(self, data):
        result = self.checkPrerequisites(data)
        if not result.isOk():
            return Result.fail({
                "type": "prerequisite",
                "error": result.extract(),
            })

        result = self.parseFields(data)
        if not result.isOk():
            return Result.fail({
                "type": "fields",
                "error": result.extract(),
            })
        fields = result.extract()

        result = self.consistencyCheck(fields)
        if not result.isOk():
            return Result.fail({
                "type": "consistency",
                "error": result.extract(),
            })

        return Result.success(fields)

    def checkPrerequisites(self, data):
        if not isinstance(data, dict):
            return "data must be a dictionary"

        for (field, fieldType) in self.schema.items():
            if field not in data:
                return Result.fail("field " + field + " is missing")

        return Result.success(None)

    def parseFields(self, data):
        fields = {}
        errors = {}
        errorsOccured = False

        for (field, fieldType) in self.schema.items():
            result = fieldType.create(data[field])
            if result.isOk():
                fields[field] = result.extract()
            else:
                errorsOccured = True
                errors[field] = result.extract()

        if errorsOccured:
            return Result.fail(errors)
        else:
            return Result.success(fields)

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
            return Result.success(data)
        else:
            return Result.fail("should be an integer")

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
            return Result.success(data)
        else:
            return Result.fail("should be a string")

class ListDataType:
    def __init__(self, innerType):
        self.innerType = innerType

    def equals(self, otherType):
        return isinstance(otherType, ListDataType) and self.innerType.equals(otherType.innerType)

    def serialize(self, items):
        return list(map(lambda item: self.innerType.serialize(item), items))

    def create(self, data):
        if isinstance(data, list):
            results = map(lambda inner: self.innerType.create(inner), data)
            if len([x for x in results if not x.isOk()]) == 0:
                items = list(map(lambda result: result.extract(), results))
                return Result.success(items)
            else:
                return Result.fail({
                    "type": "items",
                    "error": [None if x.isOk() else x.extract() for x in results],
                })
        else:
            return Result.fail({
                "type": "prerequisite",
                "error": "should be a list",
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
            return Result.success(data)
        else:
            return Result.fail("invalid value")
