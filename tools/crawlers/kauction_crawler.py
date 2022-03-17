import os
import time
import requests
import yaml
import json
import random
from tools.crawlers.exceptions import NeedReRequest
from tools.crawlers.credential_manager import CredentialManager


# 프로젝트에서는 한 번의 경매를 sale이라고 하지만, k-acution에서 제공하는 api주소, json 키 값등에서는 auc이라는 약어를 사용하므로
# 이 클래스에서는 파라미터 이름이나 변수 이름에서는 auc이라고 표기하고   (json 등으로 key-value 넘겨주는 과정에서 혼란 방지
# 함수 명은 sale로 표기함  (크롤러들이 같은 함수 이름을 가지도록)


class KAuctionCrawler:
    def __init__(self):
        filename = os.path.join(os.path.dirname(__file__), "crawler_properties.yaml")
        with open(filename) as crawler_properties_file:
            self.__crawler_prop = yaml.load(crawler_properties_file, Loader=yaml.FullLoader)[
                "kauction"
            ]

        filename_latest = os.path.join(os.path.dirname(__file__), "crawler_latest.yaml")
        with open(filename_latest) as crawler_latest_file:
            self.__crawler_latest = yaml.load(crawler_latest_file, Loader=yaml.FullLoader)[
                "kauction"
            ]
        # content-negotiation을 통해 lot정보의 json 데이터를 한글/영어로 제공한다.
        # 영어로 제공할 때 값이 달라지는 데이터 column들을 담고 있다.
        self.__en_col = [
            "artist_name",
            "title",
            "size",
            "material",
            "display_price_max",
            "auc_title",
            "card_message",
        ]
        # 기본 헤더 정보
        self.__headers = {
            "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json",
        }
        # kauction에서 사용하는 옥션 타입 별 코드 맵핑 정보
        self.__auc_kind_dict = {"Major": "1", "Premium": "2", "Weekly": "4"}
        self.__auc_kind_code_dict = {"1": "Major", "2": "Premium", "4": "Weekly"}

        # 옥션 타입 별 이미지 경로 정보
        self.__image_path_dict = {
            "Major": "Work/",
            "Premium": "Kmall/Work/",
            "Weekly": "Konline/Work/",
        }

        # Major 경매 Lot들은 대,중,소 3개의 크기를 제공하고 나머지는 중, 소 2가지 크기를 제공. 크롤러가 저장하는 기본값은 "M"
        self.__image_size_dict = {
            "Major": {"L": ("", ""), "M": ("T/", "_L"), "S": ("T/", "")},
            "Premium": {"L": ("", "_L"), "M": ("", "_L"), "S": ("", "")},
            "Weekly": {"L": ("", "_L"), "M": ("", "_L"), "S": ("", "")},
        }
        self.__image_formats = ("image/png", "image/jpeg", "image/jpg")
        self.__cookie = None

    # Credential Manager로 부터 생성된 cookie정보를 세팅
    def set_authorized_cookie(self, cookie_dict):
        self.__cookie = cookie_dict
        self.__headers = self.__headers | self.__cookie

    # 모든 종류 옥션의 최신 옥션 번호 크롤링
    def get_latest_sale_no(self):
        url_base = self.__crawler_prop["auction_url"]
        # 요청 시 날짜 순으로 정렬하여 최근 날짜의 경매 정보 불러오도록 파라미터 설정
        req_data = json.dumps(
            {"search": "", "page": "1", "sort_column": "auc_end_date", "sort_option": "DESC"}
        )
        latest_dict = {auc_kind: "" for auc_kind in self.__auc_kind_dict}

        for auc_kind in self.__auc_kind_dict:
            url = url_base + auc_kind
            res = requests.post(url, headers=self.__headers, data=req_data)

            if "data" not in res.json() or res.status_code != 200:
                raise NeedReRequest(res.status_code, "get_lateset_sale_no")
            latest_num = res.json()["data"][0]["auc_num"]
            latest_dict[auc_kind] = str(latest_num)
        return latest_dict

    # 경매 종류 별 새로 추가할 번호 범위 반환
    def check_sync_status(self):
        latest_dict = self.get_latest_sale_no()
        local_latest_dict = self.__crawler_latest
        return {s: (local_latest_dict[s], v) for s, v in latest_dict.items()}

    # 지정한 옥션 종류에 대해 최근 10개의 경매 정보를 불러옴. kauction에서 page별로 10개를 제공하며 페이지를 이동하여 과거 경매정보 조회 가능
    def get_sale_data(self, auc_kind, page="1"):
        url = self.__crawler_prop["auction_url"] + auc_kind
        req_data = json.dumps(
            {"search": "", "page": str(page), "sort_column": "auc_end_date", "sort_option": "DESC"}
        )
        res = requests.post(url, headers=self.__headers, data=req_data)
        auc_data = res.json()["data"]

        if (res.status_code == 200 and len(auc_data) != 10 and int(page) < 5) or (
            res.status_code != 200
        ):
            raise NeedReRequest(status_code=res.status_code)

        return auc_data

    # noinspection PyMethodMayBeStatic
    def __write_sales_latest(self, target_auc_num_dict):
        filename_latest = os.path.join(os.path.dirname(__file__), "crawler_latest.yaml")

        with open(filename_latest) as crawler_latest_file:
            crawler_latest = yaml.load(crawler_latest_file, Loader=yaml.FullLoader)

        for auc_kind, latest in target_auc_num_dict.items():
            crawler_latest["kauction"][auc_kind] = latest[1]

        crawler_latest["kauction"]["Date"] = time.strftime("%Y-%m-%d", time.localtime(time.time()))

        with open(filename_latest, "w") as crawler_latest_file:
            yaml.dump(crawler_latest, crawler_latest_file)
        return None

    # 새로 받아와야할 경매 종류 별 경매 번호 dict를 파라미터로 받아 모든 경매 정보를 받아서 저장한다.
    # target_auc_num_dict는 { 'Major':(st_auc_num,end_auc_num) } 형태이고 일반적으로 check_sync_status의 반환값이 들어갈듯
    def save_sales_data(self, target_auc_num_dict, auc_kinds_tuple=("Major", "Premium", "Weekly")):
        for auc_kind in auc_kinds_tuple:
            json_save_path = (
                os.path.dirname(__file__)
                + "/../.."
                + self.__crawler_prop["save_path_data"]
                + auc_kind
            )
            min_num, max_num = target_auc_num_dict[auc_kind]
            min_num = int(min_num)
            max_num = int(max_num)
            min_num += 1
            crawled_data = {}
            page = 1

            while min_num not in crawled_data and max_num not in crawled_data:
                auc_data = self.get_sale_data(auc_kind, str(page))
                crawled_data = crawled_data | {int(data["auc_num"]): data for data in auc_data}
                page += 1

            crawled_data = {k: v for k, v in crawled_data.items() if min_num <= k <= max_num}
            for auc_num, data in crawled_data.items():
                save_path = json_save_path + "/sale_" + str(auc_num) + ".json"
                with open(save_path, "w", encoding="utf-8") as json_file:
                    json.dump(data, json_file, indent=4, ensure_ascii=False)

        self.__write_sales_latest(target_auc_num_dict)
        return None

    # 지정한 옥션 종류, 번호에 대한 모든 lot 정보를 크롤링
    def save_lots_data(self, auc_kind, auc_num, page=1, page_size=3000):
        auc_kind_code = self.__auc_kind_dict[auc_kind]
        url = self.__crawler_prop["lot_url"] + auc_kind_code + "/" + auc_num

        headers_en = {"Content-Type": "application/json"} | self.__cookie
        req_data = json.dumps(
            {
                "page": str(page),
                "page_size": str(page_size),
                "page_type": "P",
                "auc_kind": auc_kind_code,
                "auc_num": auc_num,
            }
        )
        # 한글, 영어 각각 한번씩 요청을 보낸다
        res = requests.post(url, headers=self.__headers, data=req_data)
        res_en = requests.post(url, headers=headers_en, data=req_data)

        if (
            "data" not in res.json()
            or "data" not in res_en.json()
            or res.status_code != 200
            or res_en.status_code != 200
            or len(res.json()) != len(res_en.json())
            or len(res.json()) == 0
        ):
            # logging.error('auc kind= %s, auc_num= %s' % (auc_kind, auc_num))
            raise NeedReRequest(res.status_code, "get_lot_data")

        data = res.json()["data"]
        data_en = res_en.json()["data"]
        # 두 개의 요청의 합집합을 생성
        data_merged = [
            dt | {k + "_en": v for k, v in dte.items() if k in self.__en_col}
            for dt, dte in zip(data, data_en)
        ]

        json_save_path = (
            os.path.dirname(__file__)
            + "/../.."
            + self.__crawler_prop["save_path_data"]
            + auc_kind
            + "/lot_"
            + str(auc_num)
            + ".json"
        )
        with open(json_save_path, "w", encoding="utf-8") as json_file:
            json.dump(data_merged, json_file, indent=4, ensure_ascii=False)
        # 이미지 이름들을 반환하도록 하여 save images에서 사용
        return {
            "auc_kind": auc_kind,
            "auc_num": auc_num,
            "image_names": [_data["img_file_name"] for _data in data_merged],
        }

    # 이미지 이름을 받아 하나의 이미지 저장
    def save_single_lot_image(self, auc_kind, auc_num, image_name, size="M"):
        name, ext = image_name.split(".")
        pre, post = self.__image_size_dict[auc_kind][size]
        image_path = (
            "0" * (4 - len(str(auc_num))) + str(auc_num) + "/" + pre + name + post + "." + ext
        )
        url = self.__crawler_prop["image_url"] + self.__image_path_dict[auc_kind] + image_path
        res = requests.get(url, headers=self.__headers)

        if res.status_code != 200 or res.headers["content-type"] not in self.__image_formats:
            raise NeedReRequest(res.status_code, "save_single_lot_image")
        image_save_path = (
            os.path.dirname(__file__)
            + "/../.."
            + self.__crawler_prop["save_path_image"]
            + auc_kind
            + "/"
            + image_name
        )
        with open(image_save_path, "wb") as handler:
            handler.write(res.content)

        return image_save_path

    # 이미지 이름 list를 받아이미지 여러개 저장
    def save_sale_images(self, auc_kind, auc_num, image_names, read_file=False):
        # image names를 param으로 안받고 json으로 저장한 lot정보를 읽는 방법도 가능하도록
        if read_file:
            json_save_path = (
                os.path.dirname(__file__)
                + "/../.."
                + self.__crawler_prop["save_path_data"]
                + auc_kind
                + "/lot_"
                + str(auc_num)
                + ".json"
            )
            with open(json_save_path, "r", encoding="utf-8") as json_file:
                auc_data = json.load(json_file)
                image_names = [_data["img_file_name"] for _data in auc_data]

        for image_name in image_names:
            self.save_single_lot_image(auc_kind, auc_num, image_name)
            rand_value = random.uniform(1, self.__crawler_prop["sleep_time"])
            time.sleep(rand_value)

        return None


if __name__ == "__main__":
    cm = CredentialManager()
    cookie = cm.get_authorized_header("kauction")

    kr = KAuctionCrawler()
    kr.set_authorized_cookie(cookie)
    print(kr.get_latest_sale_no())
    kr.save_sales_data(
        {"Major": (145, 146)}, ("Major",)
    )  # kr.save_sales_data(kr.get_latest_sale_no())

    image_names = kr.save_lots_data("Major", "146")

    kr.save_sale_images(
        image_names["auc_kind"], image_names["auc_num"], image_names["image_names"][:5]
    )
