from tortoise import fields
from tortoise import models


class Record(models.Model):
    uuid = fields.UUIDField(unique=True, pk=True)
    student_name = fields.CharField(max_length=255, default="")
    student_group = fields.CharField(max_length=20, default="")
    datetime = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "records"