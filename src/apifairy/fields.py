from marshmallow import ValidationError
from marshmallow.fields import Field
from werkzeug.datastructures import FileStorage


class FileField(Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, FileStorage):
            raise ValidationError('Not a file.')
        return value
