"""
Author: rensongqi
Email: rensongqi1024@gmail.com
"""

from tortoise.models import Model
from tortoise import fields


class Operator(Model):
    id = fields.IntField(pk=True, source_field="id")
    user_id = fields.CharField(source_field="user_id", max_length=50)
    username = fields.CharField(max_length=50, source_field="username")
    password = fields.CharField(max_length=50, source_field="password")
    dept_id = fields.IntField(source_field="dept_id")
    user_class = fields.IntField(source_field="user_class")
    upload_state = fields.IntField(source_field="upload_state")

    def to_dict(self):
        return dict(user_id=self.user_id, username=self.username, user_class=self.user_class)

    # def __str__(self):
    #     return "用户登录名: {0}, 用户名: {1}, 用户级别: {2}".format(self.login_account, self.username, self.user_level)

    class Meta:
        table = "operator"  #数据表名字
        # unique_together=(["login_account"])#唯一字段
        # indexes = ("field_a", "field_b")  #索引
        # ordering = ["name", "-date_field"]   #默认排序



class WebUser(Model):
    id = fields.IntField(pk=True, source_field="id")
    user_id = fields.CharField(max_length=50, source_field="user_id")
    username = fields.CharField(max_length=50, source_field="username")
    password = fields.CharField(max_length=50, source_field="password")
    dept_id = fields.IntField(source_field="dept_id")
    menu_access = fields.CharField(max_length=200, source_field="menu_access", null=True)
    user_class = fields.IntField(source_field="user_class")
    menu_ctrl = fields.CharField(max_length=200, source_field="menu_ctrl", null=True)
    upload_state = fields.IntField(source_field="upload_state", null=True)

    def to_dict(self):
        return dict(
            id=self.id,
            user_id=self.user_id,
            username=self.username,
            password=self.password,
            dept_id=self.dept_id,
            menu_access=self.menu_access,
            user_class=self.user_class,
            menu_ctrl=self.menu_ctrl,
            upload_state=self.upload_state,
        )

    class Meta:
        table = "web_user"  # 数据表名字