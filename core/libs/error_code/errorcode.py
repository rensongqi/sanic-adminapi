"""
Author: rensongqi(）
Email: rensongqi1024@gmail.com
"""

from .enum import BaseECEnum, ECData


class ECEnum(BaseECEnum):
    """错误码枚举类"""
    Success = ECData("0", "成功")
    Fail = ECData("-1", "失败")
    # ImageDelete = ECData("")
    ServerError = ECData("500", "服务异常，请稍后重试")
    NoResourceFound = ECData("40001", "未找到资源")
    InvalidParameter = ECData("40002", "参数无效")
    AccountOrPassWordErr = ECData("40003", "账户或密码错误")
    VerificationCodeError = ECData("40004", "验证码错误")
    PleaseSignIn = ECData("40005", "请登陆")
    # WeChatAuthorizationFailure = ECData("40006", "微信授权失败")
    InvalidOrExpired = ECData("40007", "验证码过期或无效")
    # MobileNumberError = ECData("40008", "手机号错误")
    # FrequentOperation = ECData("40009", "操作频繁,请稍后再试")
    # DelayResource = ECData("40010", "资源访问受限")
    # FailOTHERLOGIN = ECData("40011", "其他地方登陆")
    FailToken = ECData("40012", "认证无效或过期")
    SessionExpired = ECData("40013", "会话过期或失效")
    # TEST = ECData("TEST", "测试错误")
