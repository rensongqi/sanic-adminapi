from tortoise.models import Model
from tortoise import fields
import core.models as models


class CardManager(Model):
    # IC卡详细信息
    id = fields.IntField(pk=True, source_field="id")                                    # id
    vehicle_no = fields.CharField(max_length=255, source_field="vehicle_no")            # 车牌号
    vehicle_door_no = fields.CharField(max_length=255, source_field="vehicle_door_no")  # 车辆自编号
    vehicle_type = fields.CharField(max_length=255, source_field="vehicle_type")        # 车辆型号
    department = fields.CharField(max_length=255, source_field="department")            # 所属单位
    ic_card_no = fields.CharField(max_length=255, source_field="ic_card_no")            # IC卡卡号
    start_time = fields.CharField(max_length=255, source_field="start_time")            # IC卡生效时间
    expire_time = fields.CharField(max_length=255, source_field="expire_time")          # IC卡失效时间
    weight_station = fields.CharField(max_length=255, source_field="weight_station")    # 该卡能进的地磅站

    def to_dict(self):
        return dict(
            id=self.id,
            vehicle_no=self.vehicle_no,
            vehicle_door_no=self.vehicle_door_no,
            vehicle_type=self.vehicle_type,
            department=self.department,
            ic_card_no=self.ic_card_no,
            start_time=self.start_time,
            expire_time=self.expire_time,
            weight_station=self.weight_station,
        )

    class Meta:
        table = "ic_card_details"            # 数据表名字
        unique_together = (["id"])           # 唯一字段


class CardChanged(Model):
    # IC卡换卡记录信息
    id = fields.IntField(pk=True, source_field="id")                                        # id
    change_card_time = fields.DatetimeField(source_field="change_card_time")                # 更换时间
    change_reason = fields.IntField(source_field="change_reason")                           # 换卡原因 1:正常损坏；2:人为损坏;3:丢失;
    user_id = fields.CharField(max_length=20, source_field="user_id")                       # 操作者
    info = fields.CharField(max_length=50, source_field="info")                             # 备注信息
    vehicle_no = fields.CharField(max_length=50, source_field="vehicle_no")                 # 车牌号
    vehicle_door_no = fields.CharField(max_length=50, source_field="vehicle_door_no")       # 车辆自编号
    upload_state = fields.IntField(max_length=255, source_field="upload_state")             # 上传状态

    card_id: fields.ForeignKeyRelation[models.Card] = fields.ForeignKeyField(
        model_name="models.Card",
        related_name="card_changed_old",
        to_field="id",
        source_field="card_id",
        null=True,
    )
    new_card_id: fields.ForeignKeyRelation[models.Card] = fields.ForeignKeyField(
        model_name="models.Card",
        related_name="card_changed_new",
        to_field="id",
        source_field="new_card_id",
        null=True,
    )
    dept_id: fields.ForeignKeyRelation[models.Department] = fields.ForeignKeyField(
        model_name="models.Department",
        related_name="card_changed",
        to_field="id",
        source_field="dept_id",
        null=True,
    )

    def to_dict(self):
        department_t = ""
        card_no_old_t = ""
        card_no_new_t = ""
        if self.card_id:
            card_no_old_t = self.card_id.card_no
        if self.new_card_id:
            card_no_new_t = self.new_card_id.card_no
        if self.dept_id:
            department_t = self.dept_id.department_name
        reason = ""
        if self.change_reason == 1:
            reason = "正常损坏"
        elif self.change_reason == 2:
            reason = "人为损坏"
        else:
            reason = "丢失"
        return dict(
            id=self.id,
            ic_card_no_old=card_no_old_t,
            ic_card_no_new=card_no_new_t,
            change_card_time=self.change_card_time,
            change_reason=reason,
            operator=self.user_id,
            remarks=self.info,
            vehicle_no=self.vehicle_no,
            vehicle_door_no=self.vehicle_door_no,
            department=department_t,
            upload_state=self.upload_state,
        )

    class Meta:
        table = "card_changed"             # 数据表名字
        unique_together = (["id"])         # 唯一字段
