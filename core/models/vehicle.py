"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""
# coding: utf-8

from tortoise.models import Model
from tortoise import fields
from datetime import datetime
import core.models as models


class Department(Model):
    id = fields.IntField(pk=True, source_field="id")
    department_code = fields.CharField(max_length=20, source_field="department_code")
    department_name = fields.CharField(max_length=50, source_field="department_name")
    department_info = fields.CharField(max_length=50, source_field="department_info") # 单位说明
    # parent_dept_id = fields.IntField(source_field="parent_dept_id")
    parent_dept_id: fields.ForeignKeyNullableRelation["Department"] = fields.ForeignKeyField(
        model_name="models.Department",
        related_name="parent_depts",
        to_field="id",
        source_field="parent_dept_id",
    )
    used = fields.IntField(source_field="used") # 使用状态
    create_time = fields.DatetimeField(source_field="create_time")
    order_id = fields.IntField(source_field="order_id")
    unit_kind = fields.IntField(source_field="unit_kind")   # 单位属性
    upload_state = fields.IntField(source_field="upload_state")
    stat = fields.IntField(source_field="stat")     # 单位统计类别
    confirm_source = fields.IntField(source_field="confirm_source")
    confirm_stat = fields.BinaryField(source_field="confirm_stat")
    type = fields.IntField(source_field="type")
    sheshi_type = fields.IntField(source_field="sheshi_type")
    max_weight_daily = fields.DecimalField(max_digits=10, decimal_places=2, source_field="max_weight_daily")

    vehicles: fields.ReverseRelation["Vehicle"]
    pounds: fields.ReverseRelation["Pound"]
    operators: fields.ReverseRelation["Operator"]
    web_users: fields.ReverseRelation["WebUser"]
    drivers: fields.ReverseRelation["Driver"]
    parent_depts: fields.ReverseRelation["Department"]
    card_changed: fields.ReverseRelation["models.CardChanged"]

    def to_dict(self):
        return dict(
            id=self.id,
            department_code=self.department_code,
            department_name=self.department_name,
            department_info=self.department_info,
            # parent_dept_id=self.parent_dept_id,
            used=self.used,
            # create_time=self.create_time,
            # order_id=self.order_id,
            unit_kind=self.unit_kind,
            # upload_state=self.upload_state,
            stat=self.stat,
            # confirm_source=self.confirm_source,
            # confirm_stat=self.confirm_stat,
            # type=self.type,
            # sheshi_type=self.sheshi_type,
            # max_weight_daily=self.max_weight_daily,
        )

    class Meta:
        table = "department"  # 数据表名字


class Pound(Model):
    # 地磅站信息
    id = fields.IntField(pk=True, source_field="id")  # 地磅站id
    comp_name = fields.CharField(max_length=255, source_field="comp_name")  # 地磅站名称
    pound_no = fields.CharField(max_length=255, source_field="pound_no")  # 地磅站编号
    comments = fields.TextField(source_field="comments")  # 备注
    modify_time = fields.DatetimeField(source_field="modify_time", default=datetime.now())  # 修改时间
    modify_state = fields.IntField(source_field="modify_state")  # 修改状态
    upload_state = fields.IntField(source_field="upload_state")  # 上传状态
    dept_id: fields.ForeignKeyRelation[Department] = fields.ForeignKeyField(
        model_name="models.Department",
        related_name="pounds",
        to_field="id",
        source_field="dept_id",
        null=True,
    )

    card_pound: fields.ReverseRelation["CardPound"]
    weight_records: fields.ReverseRelation["WeightRecord"]

    def to_dict(self):
        return dict(
            id=self.id,
            comp_name=self.comp_name,
            pound_no=self.pound_no,
            comments=self.comments,
            # dept_id=self.dept_id,
            department_name=self.dept_id.department_name,
            modify_time=self.modify_time,
        )

    class Meta:
        table = "pound"  # 数据表名字
        unique_together = (["id"])  # 唯一字段


class Card(Model):
    id = fields.IntField(pk=True, source_field="id")  # id
    card_no = fields.CharField(max_length=100, source_field="card_no")  # IC卡编号
    card_start_time = fields.DateField(source_field="card_start_time")  # IC卡生效时间
    card_expire_time = fields.DateField(source_field="card_expire_time")  # IC卡过期时间
    num_card_invalid = fields.IntField(source_field="num_card_invalid")  # 是否是临时卡
    upload_state = fields.IntField(source_field="upload_state")  # 上传状态
    modify_state = fields.IntField(source_field="modify_state")  # 修改状态
    change_reason = fields.CharField(max_length=100, source_field="change_reason")  # 改变原因
    card_print_no = fields.CharField(max_length=100, source_field="card_print_no")  # IC卡印刷号

    vehicles: fields.ReverseRelation["Vehicle"]
    card_pound: fields.ReverseRelation["CardPound"]
    card_changed_old: fields.ReverseRelation["models.CardChanged"]
    card_changed_new: fields.ReverseRelation["models.CardChanged"]

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

    def vehicle_to_dict(self):
        vehicle_no_t = ""
        vehicle_door_no_t = ""
        if self.vehicles:
            vehicle_no_t = self.vehicles[0].vehicle_no
            vehicle_door_no_t = self.vehicles[0].vehicle_door_no
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
            vehicle_no=vehicle_no_t,
            vehicle_door_no=vehicle_door_no_t,
        )

    class Meta:
        table = "card"  # 数据表名字
        unique_together = (["id"])  # 唯一字段


class CardPound(Model):
    # IC卡换卡记录信息
    id = fields.IntField(pk=True, source_field="id")  # id
    card_id: fields.ForeignKeyRelation[Card] = fields.ForeignKeyField(
        model_name="models.Card",
        related_name="card_pound",
        to_field="id",
        source_field="card_id",
    )  # IC卡id
    pound_id: fields.ForeignKeyRelation[Pound] = fields.ForeignKeyField(
        model_name="models.Pound",
        related_name="card_pound",
        to_field="id",
        source_field="pound_id",
    )  # 该IC卡可以进的地磅站id
    upload_state = fields.IntField(max_length=255, source_field="upload_state")  # 上传状态

    vehicles: fields.ReverseRelation["Vehicle"]
    card_pound: fields.ReverseRelation["Card"]

    def to_dict(self):
        return dict(
            id=self.id,
            card_id=self.card_id,
            pound_id=self.pound_id,
            upload_state=self.upload_state,
        )

    class Meta:
        table = "card_pound"  # 数据表名字
        unique_together = (["id"])  # 唯一字段


class VehicleType(Model):
    id = fields.IntField(pk=True, source_field="id")
    vehicle_type_no = fields.IntField(source_field="vehicle_type_no")
    vehicle_type_name = fields.CharField(max_length=50, source_field="vehicle_type_name")
    modify_state = fields.IntField(source_field="modify_state")
    modify_time = fields.DatetimeField(source_field="modify_time")
    vehicle_type_info = fields.CharField(max_length=100, source_field="vehicle_type_info", null=True)
    upload_state = fields.IntField(source_field="upload_state")

    vehicles: fields.ReverseRelation["Vehicle"]

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


class GarbageType(Model):
    id = fields.IntField(pk=True, source_field="id")
    garbage_type_no = fields.CharField(max_length=2, source_field="garbage_type_no")
    garbage_type_name = fields.CharField(max_length=50, source_field="garbage_type_name")
    garbage_price = fields.DecimalField(max_digits=10, decimal_places=2, source_field="garbage_price")
    modify_state = fields.IntField(source_field="modify_state")
    modify_time = fields.DatetimeField(source_field="modify_time")
    garbage_type_info = fields.CharField(max_length=50, source_field="garbage_type_info", null=True)
    upload_state = fields.IntField(source_field="upload_state", null=True)

    vehicles: fields.ReverseRelation["Vehicle"]
    weight_records: fields.ReverseRelation["WeightRecord"]

    def to_dict(self):
        return dict(
            id=self.id,
            garbage_type_no=self.garbage_type_no,
            garbage_type_name=self.garbage_type_name,
            garbage_price=self.garbage_price,
            modify_state=self.modify_state,
            modify_time=self.modify_time,
            garbage_type_info=self.garbage_type_info,
            upload_state=self.upload_state,
        )

    # def __str__(self):
    #     return "车辆型号: {0}".format(self.vehicle_type_name)

    class Meta:
        table = "garbage_type"  # 数据表名字


class Region(Model):
    id = fields.IntField(pk=True, source_field="id")
    region_name = fields.CharField(source_field="region_name", max_length=50)
    upload_state = fields.IntField(source_field="upload_state", null=True)
    order_no = fields.CharField(source_field="order_no", max_length=50, null=True)

    garbage_sources: fields.ReverseRelation["GarbageSource"]

    def __str__(self):
        return self.id

    def to_dict(self):
        return dict(
            id=self.id,
            region_name=self.region_name,
            upload_state=self.upload_state,
            order_no=self.order_no
        )

    # def __str__(self):
    #     return "用户登录名: {0}, 用户名: {1}, 用户级别: {2}".format(self.login_account, self.username, self.user_level)

    class Meta:
        table = "region"  # 数据表名字


class GarbageSource(Model):
    id = fields.IntField(pk=True, source_field="id")
    source_name = fields.CharField(max_length=50, source_field="source_name")
    source_flag = fields.IntField(source_field="source_flag")
    info = fields.CharField(max_length=50, source_field="info")
    upload_state = fields.IntField(source_field="upload_state")
    source_id = fields.IntField(source_field="source_id", null=True)
    code = fields.IntField(source_field="code", null=True)
    region_id: fields.ForeignKeyRelation[Region] = fields.ForeignKeyField(
        "models.Region", related_name="garbage_sources", source_field="region_id"
    )
    virtual_source = fields.CharField(max_length=50, source_field="virtual_source", null=True)
    vehicles: fields.ReverseRelation["Vehicle"]
    weight_records: fields.ReverseRelation["WeightRecord"]

    # weight_records: fields.ReverseRelation["WeightRecord"]

    def __str__(self):
        return self.source_name

    def to_dict(self):
        region_name = self.region_id.region_name if self.region_id else ""
        return dict(
            id=self.id,
            source_name=self.source_name,
            source_flag=self.source_flag,
            info=self.info,
            upload_state=self.upload_state,
            source_id=self.source_id,
            code=self.code,
            region_name=region_name,
            virtual_source=self.virtual_source,
        )

    # def __str__(self):
    #     return "用户登录名: {0}, 用户名: {1}, 用户级别: {2}".format(self.login_account, self.username, self.user_level)

    class Meta:
        table = "garbage_source"  # 数据表名字
        # unique_together = (["source_name"])  # 唯一字段


class Vehicle(Model):
    id = fields.IntField(pk=True, source_field="id")
    vehicle_no = fields.CharField(source_field="vehicle_no", max_length=50)
    vehicle_door_no = fields.CharField(source_field="vehicle_door_no", max_length=20)

    dept_id: fields.ForeignKeyRelation[Department] = fields.ForeignKeyField(
        model_name="models.Department",
        related_name="vehicles",
        to_field="id",
        source_field="dept_id",
    )

    vehicle_type_id: fields.ForeignKeyRelation[VehicleType] = fields.ForeignKeyField(
        model_name="models.VehicleType",
        related_name="vehicles",
        to_field="id",
        source_field="vehicle_type_id",
    )

    tare_weight = fields.DecimalField(max_digits=10, decimal_places=2, source_field="tare_weight")
    max_net_weight = fields.DecimalField(max_digits=10, decimal_places=2, source_field="max_net_weight")
    modify_state = fields.IntField(source_field="modify_state", null=True)
    modify_time = fields.DatetimeField(source_field="modify_time", null=True, )
    vehicle_info = fields.CharField(max_length=50, source_field="vehicle_info", null=True)

    card_id: fields.ForeignKeyRelation[Card] = fields.ForeignKeyField(
        model_name="models.Card",
        related_name="vehicles",
        to_field="id",
        source_field="card_id",
        null=True,
    )

    upload_state = fields.IntField(source_field="upload_state", null=True)
    vehicle_use = fields.CharField(max_length=50, source_field="vehicle_use", null=True)
    driver = fields.CharField(max_length=50, source_field="driver", null=True)
    buy_time = fields.DateField(source_field="buy_time", null=True)
    buy_cost = fields.DecimalField(max_digits=10, decimal_places=2, source_field="buy_cost", null=True)

    garbage_type_id: fields.ForeignKeyRelation[GarbageType] = fields.ForeignKeyField(
        model_name="models.GarbageType",
        related_name="vehicles",
        to_field="id",
        source_field="garbage_type_id",
        null=True,
    )
    garbage_source_id: fields.ForeignKeyRelation[GarbageSource] = fields.ForeignKeyField(
        model_name="models.GarbageSource",
        related_name="vehicles",
        to_field="id",
        source_field="garbage_source_id",
        null=True,
    )

    weight_records: fields.ReverseRelation["WeightRecord"]

    def to_dict(self):
        # print(
        #     self.id,
        #     self.dept_id,
        #     self.vehicle_type_id,
        #     self.card_id,
        #     self.garbage_type_id,
        #     self.garbage_source_id,
        # )
        card_no = self.card_id.card_no if self.card_id else ""
        department_name = self.dept_id.department_name if self.dept_id else ""
        vehicle_type_name = self.vehicle_type_id.vehicle_type_name if self.vehicle_type_id else ""
        garbage_type_name = self.garbage_type_id.garbage_type_name if self.garbage_type_id else ""
        garbage_source_name = self.garbage_source_id.source_name if self.garbage_source_id else ""

        return dict(
            id=self.id,
            vehicle_no=self.vehicle_no,
            vehicle_door_no=self.vehicle_door_no,
            department_name=department_name,
            vehicle_type_name=vehicle_type_name,
            tare_weight=self.tare_weight,
            max_net_weight=self.max_net_weight,
            modify_state=self.modify_state,
            modify_time=self.modify_time,
            vehicle_info=self.vehicle_info,
            card_no=card_no,
            upload_state=self.upload_state,
            vehicle_use=self.vehicle_use,
            driver=self.driver,
            # buy_time=self.buy_time,
            buy_cost=self.buy_cost,
            garbage_type_name=garbage_type_name,
            garbage_source_name=garbage_source_name,
        )

    def card_to_dict(self, pound_name):
        card_no_t = ""
        card_start_time_t = ""
        card_expire_time_t = ""
        dep_name_t = ""
        garbage_type_name_t = ""
        garbage_source_name_t = ""
        vehicle_type_name_t = ""
        if self.card_id:
            card_no_t = self.card_id.card_no
            card_start_time_t = self.card_id.card_start_time
            card_expire_time_t = self.card_id.card_expire_time
        if self.dept_id:
            dep_name_t = self.dept_id.department_name
        if self.vehicle_type_id:
            vehicle_type_name_t = self.vehicle_type_id.vehicle_type_name
        if self.garbage_type_id:
            garbage_type_name_t = self.garbage_type_id.garbage_type_name
        if self.garbage_source_id:
            garbage_source_name_t = self.garbage_source_id.source_name
        return dict(
            vehicle_no=self.vehicle_no,
            vehicle_door_no=self.vehicle_door_no,
            dept_name=dep_name_t,
            vehicle_type_name=vehicle_type_name_t,
            tare_weight=self.tare_weight,
            max_net_weight=self.max_net_weight,
            modify_state=self.modify_state,
            modify_time=self.modify_time,
            vehicle_info=self.vehicle_info,
            card_no=card_no_t,
            card_start_time_t=card_start_time_t,
            card_expire_time_t=card_expire_time_t,
            upload_state=self.upload_state,
            vehicle_use=self.vehicle_use,
            driver=self.driver,
            pound_name=pound_name,
            garbage_type_name=garbage_type_name_t,
            garbage_source_name=garbage_source_name_t
        )

    class Meta:
        table = "vehicle"  # 数据表名字
        # unique_together=(["id"])#唯一字段
        # indexes = ("field_a", "field_b")  #索引
        # ordering = ["name", "-date_field"]   #默认排序


class Dictionary(Model):
    id = fields.IntField(pk=True, source_field="id")
    data_type = fields.CharField(max_length=50, source_field="data_type")
    data_value = fields.CharField(max_length=50, source_field="data_value")
    order_no = fields.IntField(source_field="order_no", null=True)

    def to_dict(self):
        return dict(
            id=self.id,
            data_type=self.data_type,
            data_value=self.data_value,
            order_no=self.order_no,
        )

    class Meta:
        table = 'dictionary'


class Driver(Model):
    id = fields.IntField(pk=True, source_field="id")
    driver_no = fields.CharField(source_field="driver_no", max_length=50)
    driver_name = fields.CharField(source_field="driver_name", max_length=50)
    dept_id: fields.ForeignKeyRelation[Department] = fields.ForeignKeyField(
        model_name="models.Department",
        related_name="drivers",
        to_field="id",
        source_field="dept_id",
    )
    upload_state = fields.IntField(source_field="upload_state")
    is_bind = fields.IntField(source_field="is_bind", null=True)
    weight_records: fields.ReverseRelation["WeightRecord"]

    def to_dict(self):
        dept_name = ""
        if self.dept_id:
            dept_name = self.dept_id.department_name
        return dict(
            id=self.id,
            driver_no=self.driver_no,
            driver_name=self.driver_name,
            dept_name=dept_name,
            upload_state=self.upload_state,
            is_bind=self.is_bind,
        )

    class Meta:
        table = "driver"


class Operator(Model):
    id = fields.IntField(pk=True, source_field="id")
    user_id = fields.CharField(source_field="user_id", max_length=50, unique=True)
    username = fields.CharField(max_length=50, source_field="username")
    password = fields.CharField(max_length=50, source_field="password")
    dept_id: fields.ForeignKeyRelation[Department] = fields.ForeignKeyField(
        model_name="models.Department",
        related_name="operators",
        to_field="id",
        source_field="dept_id",
    )
    user_class = fields.IntField(source_field="user_class")
    upload_state = fields.IntField(source_field="upload_state")

    weight_records: fields.ReverseRelation["WeightRecord"]

    def to_dict(self):
        dept_name = ""
        if self.dept_id:
            dept_name = self.dept_id.department_name
        return dict(
            id=self.id,
            user_id=self.user_id,
            username=self.username,
            dept_name=dept_name,
            user_class=self.user_class,
            upload_state=self.upload_state,
        )
    # def __str__(self):
    #     return "用户登录名: {0}, 用户名: {1}, 用户级别: {2}".format(self.login_account, self.username, self.user_level)

    class Meta:
        table = "operator"  # 数据表名字
        unique_together = (["user_id"])  # 唯一字段
        # indexes = ("field_a", "field_b")  #索引
        # ordering = ["name", "-date_field"]   #默认排序


class UserMenu(Model):
    id = fields.IntField(pk=True, source_field="id")
    menu_name = fields.CharField(source_field="menu_name", max_length=50)
    menu_url = fields.CharField(source_field="menu_url", max_length=100)
    menu_order = fields.IntField(source_field="menu_order")
    hidden = fields.IntField(source_field="hidden")
    # parent_id = fields.IntField(source_field="parent_id", null=True)
    parent_id: fields.ForeignKeyNullableRelation["UserMenu"] = fields.ForeignKeyField(
        model_name="models.UserMenu",
        related_name="parent_pages",
        to_field="id",
        source_field="parent_id",
        null=True,
    )
    parent_pages: fields.ReverseRelation["UserMenu"]

    def to_dict(self):
        return dict(
            id=self.id,
            menu_name=self.menu_name,
            menu_url=self.menu_url,
            menu_order=self.menu_order,
            hidden=self.hidden,
            parent_id=self.parent_id,
        )

    class Meta:
        table = "user_menu"


class WebUser(Model):
    id = fields.IntField(pk=True, source_field="id")
    user_id = fields.CharField(max_length=50, source_field="user_id")
    username = fields.CharField(max_length=50, source_field="username")
    password = fields.CharField(max_length=50, source_field="password")
    # dept_id = fields.IntField(source_field="dept_id")
    dept_id: fields.ForeignKeyNullableRelation["Department"] = fields.ForeignKeyField(
        model_name="models.Department",
        related_name="web_users",
        to_field="id",
        source_field="dept_id",
    )
    menu_access = fields.CharField(max_length=200, source_field="menu_access", null=True)
    user_class = fields.IntField(source_field="user_class")
    menu_ctrl = fields.CharField(max_length=200, source_field="menu_ctrl", null=True)
    upload_state = fields.IntField(source_field="upload_state", null=True)
    menus = fields.CharField(max_length=500,source_field="menus", null=True)

    def to_dict(self):
        dept_name = ""
        if self.dept_id:
            dept_name = self.dept_id.department_name
        return dict(
            id=self.id,
            user_id=self.user_id,
            username=self.username,
            dept_name=dept_name,
            user_class=self.user_class,
            upload_state=self.upload_state,
            menus=self.menus
        )

    class Meta:
        table = "web_user"  # 数据表名字


class WeightRecord(Model):
    id = fields.IntField(pk=True, source_field="id")
    vehicle_id: fields.ForeignKeyRelation[Vehicle] = fields.ForeignKeyField(
        model_name="models.Vehicle",
        related_name="weight_records",
        to_field="id",
        source_field="vehicle_id",
        null=True,
    )

    box_id = fields.IntField(source_field="box_id", null=True)
    time_loading = fields.DatetimeField(source_field="time_loading", null=True)

    garbage_source_id: fields.ForeignKeyRelation[GarbageSource] = fields.ForeignKeyField(
        model_name="models.GarbageSource",
        related_name="weight_records",
        to_field="id",
        source_field="garbage_source_id",
        null=True,
    )
    garbage_type_id: fields.ForeignKeyRelation[GarbageType] = fields.ForeignKeyField(
        model_name="models.GarbageType",
        related_name="weight_records",
        to_field="id",
        source_field="garbage_type_id",
        null=True,
    )

    load_meter_pos_id = fields.IntField(source_field="load_meter_pos_id", null=True)
    weight_gross = fields.DecimalField(max_digits=10, decimal_places=2, source_field="weight_gross")
    time_weight = fields.DatetimeField(source_field="time_weight")
    time_leave = fields.DatetimeField(source_field="time_leave", null=True)
    operator_id = fields.IntField(source_field="operator_id")

    driver_id: fields.ForeignKeyRelation[Driver] = fields.ForeignKeyField(
        model_name="models.Driver",
        related_name="weight_records",
        to_field="id",
        source_field="driver_id",
        null=True,
    )
    data_mark = fields.IntField(source_field="data_mark")
    weight_tare = fields.DecimalField(max_digits=10, decimal_places=2, source_field="weight_tare", null=True)
    info = fields.CharField(max_length=200, source_field="info", null=True)
    image_in = fields.CharField(max_length=200, source_field="image_in", null=True)
    image_out = fields.CharField(max_length=200, source_field="image_out", null=True)
    check_time = fields.DatetimeField(source_field="check_time", null=True)
    id_center = fields.IntField(source_field="id_center")
    # pound_id = fields.IntField(source_field="pound_id", null=True)
    pound_id: fields.ForeignKeyRelation[Pound] = fields.ForeignKeyField(
        model_name="models.Pound",
        related_name="weight_records",
        to_field="id",
        source_field="pound_id",
        null=True,
    )

    upload_state = fields.IntField(source_field="upload_state", null=True)

    # user_id: fields.ForeignKeyRelation[Operator] = fields.ForeignKeyField(
    #     model_name="models.Operator",
    #     related_name="weight_records",
    #     to_field="id",
    #     source_field="user_id",
    # )
    user_id: fields.ForeignKeyRelation[Operator] = fields.ForeignKeyField(
        model_name="models.Operator",
        related_name="weight_records",
        to_field="user_id",
        source_field="user_id",
    )
    # user_id = fields.CharField(max_length=20, source_field="user_id")
    source_manager = fields.CharField(max_length=50, source_field="source_manager", null=True)
    check_reason = fields.CharField(max_length=100, source_field="check_reason", null=True)
    memo = fields.CharField(max_length=200, source_field="memo", null=True)

    def to_dict(self):
        vehicle_no = ""
        vehicle_door_no = ""
        driver_name = ""
        dept_name = ""
        weight_checker = ""  # 有operator就取出，没有直接user_id
        garbage_source_name = ""
        garbage_type_name = ""
        region_name = ""
        data_type = ""
        loading_rate = 0.00
        pound_name = ""
        if self.vehicle_id:
            vehicle_no = self.vehicle_id.vehicle_no
            vehicle_door_no = self.vehicle_id.vehicle_door_no
            dept_name = self.vehicle_id.dept_id.department_name
            loading_rate = (self.weight_gross - self.weight_tare) / self.vehicle_id.max_net_weight
            loading_rate = "%.2f" % (loading_rate * 100) + "%"

        if self.driver_id:
            driver_name = self.driver_id.driver_name
        if self.garbage_source_id:
            garbage_source_name = self.garbage_source_id.source_name
            region_name = self.garbage_source_id.region_id.region_name
        if self.garbage_type_id:
            garbage_type_name = self.garbage_type_id.garbage_type_name
        if self.user_id:
            weight_checker = self.user_id.username
        else:
            weight_checker = self.user_id
        if self.pound_id:
            pound_name = self.pound_id.comp_name



        if self.data_mark == 0:
            data_type = "自动读取"
        if self.data_mark == 1:
            data_type = "手动补充"
        if self.data_mark == 2:
            data_type = "读卡失败后手动输入车门号"

        return dict(

            # id=self.id,
            id_center=self.id_center,
            vehicle_no=vehicle_no,
            driver_name=driver_name,
            vehicle_door_no=vehicle_door_no,
            time_weight=self.time_weight,
            weight_gross=self.weight_gross,
            time_leave=self.time_leave,
            weight_tare=self.weight_tare,
            weight_net=self.weight_gross - self.weight_tare,
            loading_rate=loading_rate,
            pound_name=pound_name,
            dept_name=dept_name,
            weight_checker=weight_checker,
            garbage_source_name=garbage_source_name,
            garbage_type_name=garbage_type_name,
            region_name=region_name,
            data_type=data_type,
            image_in="无图片",
            image_out="无图片",

            # box_id=self.box_id,
            time_loading=self.time_loading,
            # garbage_source_id=self.garbage_source_id,
            # garbage_type_id=self.garbage_type_id,
            load_meter_pos_id=self.load_meter_pos_id,
            # operator_id=self.operator_id,
            info=self.info,
            check_time=self.check_time,
            # pound_id=self.pound_id,
            # upload_state=self.upload_state,
            # user_id=self.user_id,
            # source_manager=self.source_manager,
            # check_reason=self.check_reason,
            # memo=self.memo,
        )

    def to_full_dict(self):
        region_name = ""
        garbage_source = ""
        if hasattr(self, "to_attr_source") and self.garbage_source is not None:
            region_name = self.to_attr_source.region.region_name
        if hasattr(self.garbage_source, "to_dict"):
            garbage_source = self.garbage_source.source_name

        return dict(
            id=self.id,
            record_no=self.record_no,
            flow_no=self.flow_no,
            facility=self.facility,
            driver=self.driver,
            vehicle_no=self.vehicle_no,
            vehicle_type=self.vehicle_type,
            trans_dept=self.trans_dept,
            shift_type=self.shift_type,
            computer_name=self.computer_name,
            weight_checker=self.weight_checker,
            instrument_no=self.instrument_no,
            import_status=self.import_status,
            weight_gross=self.weight_gross,
            weight_tare=self.weight_tare,
            weight_net=self.weight_net,
            weight_deduction=self.weight_deduction,
            billing_unit=self.billing_unit,
            billing_total=self.billing_total,
            time_loading=self.time_loading,
            time_weightingG=self.time_weightingG,
            time_weightingT=self.time_weightingT,
            time_weightingN=self.time_weightingN,
            memo=self.memo,
            record_status=self.record_status,
            record_created_time=self.record_created_time,
            record_creator_id=self.record_creator_id,
            field_no=self.field_no,
            input_type=self.input_type,
            garbage_type=self.garbage_type,
            record_version=self.record_version,
            vehicle_door_no=self.vehicle_door_no,
            department_sta=self.department_sta,
            time_photo=self.time_photo,
            driver_id=self.driver_id,
            garbage_source=garbage_source,
            region_name=region_name,
        )

    class Meta:
        table = "weight_record"  #
