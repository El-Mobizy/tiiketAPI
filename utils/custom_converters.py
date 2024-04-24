from werkzeug.routing import BaseConverter
import uuid

class UuidConverter(BaseConverter):
    def to_python(self, value):
        try:
            return uuid.UUID(value)
        except ValueError:
            raise ValueError(f'Invalid UUID: {value}')

    def to_url(self, value):
        if not isinstance(value, uuid.UUID):
            raise ValueError(f'Invalid UUID: {value}')
        return str(value)
