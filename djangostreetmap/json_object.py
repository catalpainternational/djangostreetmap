from ast import Expression
from typing import List, Union

from django.contrib.gis.db import models
from django.db.models import Func, Value, F


class JSONObject(Func):
    """
    This is backported from Django 4
    to provide an easier way to generate the "Properties" dict
    """

    function = "JSONB_BUILD_OBJECT"
    output_field = models.JSONField()

    def __init__(self, **fields: Union[F, Expression, str]):
        expressions = []  # type: List[Union[Value, Union[F, Expression, str]]]
        for key, value in fields.items():
            expressions.extend((Value(key), value))
        super().__init__(*expressions)

    def as_postgresql(self, compiler, connection, **extra_context):
        return self.as_sql(
            compiler,
            connection,
            function="JSONB_BUILD_OBJECT",
            **extra_context,
        )
