"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8
from pypika import CustomFunction
from tortoise.expressions import F, Function

class TruncDateTime(Function):
    database_func = CustomFunction("DATE_FORMAT", ["name", "dt_format"])

# sql = Task.all().annotate(date=TruncMonth('created_at', '%Y-%m-%d')).values('date').sql()
# print(sql)
# SELECT DATE_FORMAT(`created_at`,'%Y-%m-%d') `date` FROM `task`
