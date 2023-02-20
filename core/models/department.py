"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from tortoise.models import Model
from tortoise import fields
import core.models as models


class Department(Model):
    id = fields.IntField(pk=True, source_field="id")
    department_code = fields.CharField(max_length=20,source_field="department_code")
    department_name = fields.CharField(max_length=50,source_field="department_name")
    department_info = fields.CharField(max_length=50,source_field="department_info")
    parent_dept_id = fields.IntField(source_field="parent_dept_id")
    used = fields.IntField(source_field="used")
    create_time = fields.DatetimeField(source_field="create_time")
    order_id = fields.IntField(source_field="order_id")
    unit_kind = fields.IntField(source_field="unit_kind")
    upload_state = fields.IntField(source_field="upload_state")
    stat = fields.IntField(source_field="stat")
    confirm_source = fields.IntField(source_field="confirm_source")
    confirm_stat = fields.BinaryField(source_field="confirm_stat")
    type = fields.IntField(source_field="type")
    sheshi_type = fields.IntField(source_field="sheshi_type")
    max_weight_daily = fields.DecimalField(max_digits=10, decimal_places=2,source_field="max_weight_daily")

    vehicles: fields.ReverseRelation["models.Vehicle"]
    pounds: fields.ReverseRelation["models.Pound"]

    def to_dict(self):
        return dict(
            id=self.id,
            department_code=self.department_code,
            department_name=self.department_name,
            department_info=self.department_info,
            parent_dept_id=self.parent_dept_id,
            used=self.used,
            create_time=self.create_time,
            order_id=self.order_id,
            unit_kind=self.unit_kind,
            upload_state=self.upload_state,
            stat=self.stat,
            confirm_source=self.confirm_source,
            confirm_stat=self.confirm_stat,
            type=self.type,
            sheshi_type=self.sheshi_type,
            max_weight_daily=self.max_weight_daily,
        )

    class Meta:
        table = "department"  # 数据表名字