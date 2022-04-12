import sqlalchemy


class IntEnum(sqlalchemy.TypeDecorator):
    impl = sqlalchemy.SmallInteger()

    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):

        if isinstance(value, int):
            return value

        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)