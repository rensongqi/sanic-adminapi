"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from tortoise.models import Model
from tortoise import fields
import core.models as models

class Card(Model):
    id = fields.IntField(source_field="id")
    card_no = fields.CharField(max_length=100,source_field="card_no")
    card_start_time = fields.DatetimeField(source_field="card_start_time", null=True)
    card_expire_time = fields.DatetimeField(source_field="card_expire_time", null=True)
    num_card_invalid = fields.IntField(source_field="num_card_invalid")
    upload_state = fields.IntField(source_field="upload_state", null=True)
    modify_state = fields.IntField(source_field="modify_state")
    change_reason = fields.CharField(max_length=100,source_field="change_reason", null=True)
    card_print_no = fields.CharField(max_length=100,source_field="card_print_no", null=True)

    vehicles: fields.ReverseRelation["models.Vehicle"]

    def to_dict(self):
        return dict(
            id=self.id,
            card_no=self.card_no,
            card_start_time=self.card_start_time,
            card_expire_time=self.card_expire_time,
            num_card_invalid=self.num_card_invalid,
            upload_state=self.upload_state,
            modify_state=self.modify_state,
            change_reason=self.change_reason,
            card_print_no=self.card_print_no,
        )

    class Meta:
        table = "card"  # 数据表名字