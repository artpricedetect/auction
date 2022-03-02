class LoginFailed(Exception):
    def __init__(self):
        super().__init__("Login에 실패하였습니다.")


class NeedReRequest(Exception):
    def __init__(self, status_code="", message=""):
        text = "재요청이 필요합니다."
        if status_code:
            text += " status code = " + str(status_code) + ". "
        text += message
        super().__init__(text)
