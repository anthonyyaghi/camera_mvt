from enum import Enum, auto, unique
import omni.ui as ui

@unique
class FieldType(Enum):
    STRING_FIELD = auto(),
    INT_FIELD = auto(),
    FLOAT_FIELD = auto()


FIELDS = {FieldType.STRING_FIELD: ui.StringField, FieldType.INT_FIELD: ui.IntDrag, FieldType.FLOAT_FIELD: ui.FloatDrag}