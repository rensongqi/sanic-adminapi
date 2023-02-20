"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from tortoise.models import Model
from tortoise import fields
import core.models as models

class VehicleType(Model):
    id = fields.IntField(pk=True, source_field="id")
    vehicle_type_no = fields.IntField(source_field="vehicle_type_no")
    vehicle_type_name = fields.CharField(max_length=50, source_field="vehicle_type_name")
    modify_state = fields.IntField(source_field="modify_state")
    modify_time = fields.DatetimeField(source_field="modify_time")
    vehicle_type_info = fields.CharField(max_length=100, source_field="vehicle_type_info", null=True)
    upload_state = fields.IntField(source_field="upload_state")

    vehicles: fields.ReverseRelation["models.Vehicle"]

    def to_dict(self):
        return dict(
            id=self.id,
            vehicle_type_no=self.vehicle_type_no,
            vehicle_type_name=self.vehicle_type_name,
            modify_state=self.modify_state,
            modify_time=self.modify_time,
            vehicle_type_info=self.vehicle_type_info,
            upload_state=self.upload_state,
        )

    # def __str__(self):
    #     return "车辆型号: {0}".format(self.vehicle_type_name)

    class Meta:
        table = "vehicle_type"  # 数据表名字
        # unique_together = (["vehicle_type_name"])  # 唯一字段
        # indexes = ("field_a", "field_b")  #索引
        # ordering = ["name", "-date_field"]   #默认排序
