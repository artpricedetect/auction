import sys, os

# parent module 참조할 경우 필요한 코드
sys.path.append(os.getcwd())

from tools.alarm import alarm
from credential_manager import CredentialManager
from seoulauction_data_crawler import SeoulAuctionDataCrawler
from exceptions import NeedReRequest, LoginFailed
from tenacity import (
    retry,
    retry_if_exception_type,
    retry_if_result,
    wait_fixed,
    stop_after_attempt,
)
import yaml, logging

# 로그 생성
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class CrawlerManager:
    def __init__(self):

        # 매니지 할 크롤러 객체들을 attribute로 생성
        self.alarm_manager = alarm.AlarmManager()
        self.credential_manager = CredentialManager()
        self.seoul_crawler = SeoulAuctionDataCrawler()

        # 초기 Auth Header 설정
        self.reset_auth_headers(self.seoul_crawler)

        # Max Iteration, 재요청 시간 세팅
        filename = os.path.join(os.path.dirname(__file__), "crawler_properties.yaml")
        with open(filename) as properties_file:
            properties = yaml.load(properties_file, Loader=yaml.FullLoader)
            self.__max_iteration = properties.get("max_iteration")
            self.__re_request_time = properties.get("re_request_time")

    ####################################################################################################
    ####################################################################################################
    # Retry 과정 중 발생하는 에러 처리 콜백함수 등
    ####################################################################################################
    ####################################################################################################

    # Wrapper함수이며, 이 안에 기존 Crawler 객체들에서 작성했던 함수들을 인자로 넣어 실행하면 발생하는 오류들을 Handle
    def invoke_function(self, func):
        # 처리할 exception들 명시
        retry_exception_types = (NeedReRequest, LoginFailed)
        decorator = retry(
            stop=stop_after_attempt(self.__max_iteration),
            wait=wait_fixed(self.__re_request_time),
            # 명시되지 않은 Exception들은 다시 시도할 필요가 없으며, 재시도 하지 않고 바로 return
            retry=(retry_if_result(self.is_none) | retry_if_exception_type(retry_exception_types)),
            # Exception 발생 시 재시도 전에 진행되어야 할 콜백 함수
            after=self.failed_callback,
            # 모든 재시도 이후에도 에러 발생 시 콜백 함수: 알람 전송
            retry_error_callback=self.alarm_callback,
            reraise=True,
        )
        # https://tenacity.readthedocs.io/en/latest/
        return decorator(func)

    # 의미 없는 빈 데이터가 있을 경우 다시한번 retry할 수 있도록. 혹은 이것을 exception 으로 관리해도 됨. Return True if value is None
    def is_none(self, value):
        return value is None

    def alarm_callback(self, retry_state):
        exception = retry_state.outcome.exception()
        self.alarm_manager.alarm(str(exception))

    def failed_callback(self, retry_state):
        logger.info(f"{retry_state.fn} attempt {retry_state.attempt_number}: {retry_state.outcome}")

        # Login Failed 에러 발생 시 갱신작업 진행
        if type(retry_state.outcome.exception()) is LoginFailed:
            failed_class = retry_state.fn.__self__
            logger.info(f"Login Failed. Renewing Auth for {failed_class.organization}")
            logger.info(f"Current Headers: {failed_class.get_request_headers()}")

            self.reset_auth_headers(failed_class)
            logger.info(f"Renewed Headers: {failed_class.get_request_headers()}")

    ####################################################################################################
    ####################################################################################################
    # 아래 함수들이 실제로 서비스 상황 시 Call되는 함수들
    ####################################################################################################
    ####################################################################################################

    def test(self, organization, arg1, arg2):
        if organization == "seoulauction":
            return self.invoke_function(self.seoul_crawler.retry_test)(arg1, arg2)
        elif organization == "kauction":
            pass

    def reset_auth_headers(self, crawler):
        auth_headers = self.credential_manager.get_authorized_header(crawler.organization)
        # 각 crawler class는 organization field 를 가지고 있어야 함
        crawler.set_request_headers(auth_headers)

    def ckeck_sync_status(self, organization):
        if organization == "seoulauction":
            return self.invoke_function(self.seoul_crawler.check_sync_status)()
        elif organization == "kauction":
            pass

    def save_sales_data(self, organization, sale_identifier):
        if organization == "seoulauction":
            return self.invoke_function(self.seoul_crawler.save_sales_data)(sale_identifier)
        elif organization == "kauction":
            pass

    def save_sales_image(self, organization, sale_identifier):
        if organization == "seoulauction":
            return self.invoke_function(self.seoul_crawler.save_sale_images)(sale_identifier)
        elif organization == "kauction":
            pass


if __name__ == "__main__":
    auction_crawler = CrawlerManager()
    print(auction_crawler.test("seoulauction", 1, 2))
    print(auction_crawler.ckeck_sync_status("seoulauction"))
    # print(auction_crawler.save_sales_data("seoulauction", 689))
    # print(auction_crawler.save_sales_image("seoulauction", 689))
