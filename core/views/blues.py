# -*- coding:utf-8 -*-
"""
Author  : rensongqi
Time   : 2022-11
File   : blues.py
Description:
"""
from sanic import Blueprint
from typing import Tuple
from core.views.login.blues import bp as login_blueprint
# from core.views.admin_api.users.blues import bp as users_blueprint
from core.views.admin_api.vehicle.blues import bp as vehicle_blueprint
from core.views.admin_api.operation_logs.blues import bp as opslog_blueprint
from core.views.admin_api.vehicle_type.blues import bp as vehicle_type_blueprint
from core.views.admin_api.department.blues import bp as department_blueprint
from core.views.admin_api.weight_record.blues import bp as weight_record_blueprint
from core.views.admin_api.garbage.blues import bp as garbage_blueprint
from core.views.admin_api.region.blues import bp as region_blueprint
from core.views.admin_api.ic_card.create_records.blues import bp as ic_card_blueprint
from core.views.admin_api.ic_card.change_card.blues import bp as change_card_blueprint
from core.views.admin_api.ic_card.signed_cards.blues import bp as signed_cards_blueprint
from core.views.admin_api.ic_card.unsigned_cards.blues import bp as unsigned_cards_blueprint
from core.views.admin_api.ic_card.annual_check.blues import bp as check_blueprint
from core.views.admin_api.system.pound.blues import bp as pound_blueprint
from core.views.admin_api.users.blues import bp as user_blueprint
from core.views.admin_api.driver.blues import bp as driver_blueprint
from core.views.web_api.statistics.blues import bp as statistic_blueprint



BLUE_TUPLE: Tuple[Blueprint, ...] = (

    driver_blueprint,
    user_blueprint,
    statistic_blueprint,
    region_blueprint,
    garbage_blueprint,
    vehicle_blueprint,
    vehicle_type_blueprint,
    weight_record_blueprint,
    login_blueprint,
    opslog_blueprint,
    department_blueprint,
    ic_card_blueprint,
    change_card_blueprint,
    signed_cards_blueprint,
    unsigned_cards_blueprint,
    pound_blueprint,
    check_blueprint,
)
