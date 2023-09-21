from tortoise import fields
from tortoise import models


class Record(models.Model):
    uuid = fields.UUIDField(unique=True, pk=True)
    student_name = fields.CharField(max_length=255)
    student_group = fields.CharField(max_length=255)
    lab_name = fields.CharField(max_length=255)
    lab_date = fields.DateField()
    stream = fields.CharField(max_length=20, default="Change")
    datetime = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "records"
