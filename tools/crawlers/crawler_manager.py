from ..alarm.alarm import AlarmManager
from .credential_manager import CredentialManager
from .seoulauction_data_crawler import SeoulAuctionDataCrawler
from .exceptions import NeedReRequest, LoginFailed

import time
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_not_exception_type,
    retry_if_result,
    wait_fixed,
)

import requests
import yaml
import os
import sys

# sys.path.append('./')

# Wrapper for tenacity retry decorator
# def my_retry(func):
#     def wrapped(crawler_manager, *args, **kwargs):
#         tdecorator = retry(wait=wait_fixed(conn.retry_interval), stop=stop_after_attempt(conn.retry_count))
#         decorated = tdecorator(func)
#         return decorated(conn, *args, **kwargs)
#     return wrapped


class CrawlerManager:
    def __init__(self):

        # 매니지 할 크롤러 객체들을 attribute로 생성
        self.alarm_manager = AlarmManager()
        self.credential_manager = CredentialManager()
        self.seoul_crawler = SeoulAuctionDataCrawler()

        # 초기 Auth Header 설정
        self.__reset_auth_headers("seoulauction")

        # Max Iteration, 재요청 시간 세팅
        filename = os.path.join(os.path.dirname(__file__), "crawler_properties.yaml")
        with open(filename) as properties_file:
            properties = yaml.load(properties_file, Loader=yaml.FullLoader)
            self.__max_iteration = properties.get("max_iteration")
            self.__re_request_time = properties.get("re_request_time")

    def __alarm(self, result):
        # print("Slack or Kakao")
        self.alarm_manager.alarm("Error : " + result)

    def is_none(value):
        """Return True if value is None"""
        return value is None

    @retry
    def __reset_auth_headers(self, organization):
        auth_headers = self.credential_manager.get_authorized_header(organization=organization)

        if organization == "seoulauction":
            self.seoul_crawler.set_request_headers(auth_headers)

        elif organization == "kauction":
            pass

    @retry(
        wait=wait_fixed(3),
        # retry= ( retry_if_result(self.is_none_p) | retry_if_exception_type(NeedReRequest) )
    )
    def ckeck_sync_status(self, organization):

        if organization == "seoulauction":
            pass
        elif organization == "kauction":
            pass

    @retry
    def save_sales_data(self, organization, sale_identifier):

        if organization == "seoulauction":
            pass

        elif organization == "kauction":
            pass

    @retry
    def save_sales_image(self, organization, sale_identifier):

        if organization == "seoulauction":
            pass

        elif organization == "kauction":
            pass

    # def __is_crawler_Error(self, result):
    #     return self.__is_auth_error(result) | self.__is_request_error(result)

    # def __is_auth_error(self, result):
    #     # 앞으로 여기 내부 내용을 채워나가야 함

    #     if result.get("msg") != None:  # code 200을 제외하면 다 실패인데 200으로 해둔다면..?
    #         print(result.get("code"))
    #         print("RESULT :", result.get("msg"))
    #         if (
    #             result.get("msg")
    #             == "-1021=Timestamp for this request was 1000ms ahead of the server's time."
    #         ):
    #             print("Windows10 의 경우 시계 동기화를 실행하세요 (참고: https://rootblog.tistory.com/223)")
    #         return True
    #     else:
    #         return False

    # def __is_request_error(self, result):
    #     # 앞으로 여기 내부 내용을 채워나가야 함
    #     if "get" not in result:
    #         return False
    #     else:
    #         return False

    def invoke_readonly_function(self, method, args):
        return self.invoke_function(method, args)

    def invoke_function(self, method, args):

        success = True
        result

        for i in range(0, self.__max_iteration):
            try:
                result = method(args)

                if self.__isApiError(result):
                    print("ERROR on ", i, " th loop")
                    continue

                break

            # Error Case 1. Just request again after some seconds
            except NeedReRequest:
                time.sleep(self.__re_request_time)
                continue

            # # Error Case 2. Login Failed. Authorize again
            # except LoginFailed:
            #     self.__set_auth_headers("seoulauction")
            #     continue

            # 다시 할 필요가 없는 그 밖의 생소한 Exception들. 혹은  Break 구문 통해 바로 For문 탈출
            except Exception as other_exceptions:
                # 오류 케이스 01. (예시)
                if '"code":-4046' in other_exceptions.args[0]:
                    success = True
                    break
                # 오류 케이스 02. 잔고가 부족함 (예시)
                elif (
                    "Account has insufficient balance for requested action"
                    in other_exceptions.args[0]
                ):
                    success = True
                    # print("현물 잔고가 부족합니다.", args.get("symbol"), " -- ", args.get("quantity"))
                    break
                else:
                    success = False
                    print(other_exceptions)
                    result = str(other_exceptions.args) + " --- " + args
                    break

        if success:
            # Success
            return result
        else:
            # Fail
            self.__alarm(result)
            return "fail"
