Success = 200
Error = 500

# code= 1000... 用户模块的错误
ErrorUsernameUsed = 1001
ErrorPasswordWrong = 1002
ErrorUserNotExist = 1003
ErrorTokenExist = 1004
ErrorTokenRuntime = 1005
ErrorTokenWrong = 1006
ErrorTokenTypeWrong = 1007
ErrorUserNoRight = 1008

# code= 4000... 物流模块的错误
IncorrectLength = 4001
NotFound = 4002
NotSupport = 4003

# code= 500...
VerificationFailure = 5001

code_msg = {
    Success: "SUCCESS",
    Error: "FAIL",
    ErrorUsernameUsed: "用户名已存在！",
    ErrorPasswordWrong: "密码错误",
    ErrorUserNotExist: "用户不存在",
    ErrorTokenExist: "TOKEN不存在,请重新登陆",
    ErrorTokenRuntime: "TOKEN已过期,请重新登陆",
    ErrorTokenWrong: "TOKEN不正确,请重新登陆",
    ErrorTokenTypeWrong: "TOKEN格式错误,请重新登陆",
    ErrorUserNoRight: "该用户无权限",
    IncorrectLength: "物流单号长度不正确",
    NotFound: "查无此单号",
    NotSupport: "暂未支持该物流公司",
    VerificationFailure: "数据校验失败",
}


def get_error_msg(code: int) -> str:
    return code_msg[code]
