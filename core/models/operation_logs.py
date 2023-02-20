"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8

from tortoise.models import Model
from tortoise import fields


class OperationLog(Model):

    id = fields.IntField(pk=True, source_field="id")
    log_time = fields.DatetimeField(source_field="log_time")
    data_time = fields.DatetimeField(source_field="data_time")
    account = fields.CharField(source_field="account", max_length=20)
    username = fields.CharField(source_field="username", max_length=20)
    log_type = fields.CharField(source_field="log_type", max_length=30)
    log_info = fields.CharField(source_field="log_info", max_length=500)

    def to_dict(self):
        return dict(
            id=self.id,
            log_time=self.log_time,
            data_time=self.data_time,
            account=self.account,
            username=self.username,
            log_type=self.log_type,
            log_info=self.log_info,
        )

    class Meta:
        table = "operation_logs"  #数据表名字
