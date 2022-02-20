import requests, json, yaml, os, random, time

from credential_manager import CredentialManager


class SeoulAuctionDataCrawler:
    def __init__(self):
        # Property 파일 세팅
        filename = os.path.join(os.path.dirname(__file__), "crawler_properties.yaml")

        with open(filename) as crawler_properties_file:
            __info = yaml.load(crawler_properties_file, Loader=yaml.FullLoader).get("seoulauction")
            self.__api_url = __info.get("api_url")
            self.__img_url = __info.get("img_url")
            self.__save_path_data = __info.get("save_path_data")
            self.__save_path_image = __info.get("save_path_image")
            self.__sleep_time = __info.get("crawler_sleep_time")

        self.__request_headers = None
        self.__payload_sale = None
        self.__payload_lots = None

        # status = END 이기에 종료 경매 데이터를 읽어옴.
        # 단, 외부 기관과 같이 한 경매는 포함되지 않음 (sale_outside_yn = N)
        # 하지만, 애초에 현재 보유 경매 데이터와 가장 최근의 경매 데이터를 모두 돌며 경매 결과 정보를 읽어올 것이기에
        # 조금 늦게 반영될 수는 있어도 모두 반영되긴 할 것임
        self.__payload_latest_sale = {
            "baseParms": {"sale_kind_cd": "", "status": "END"},
            "actionList": [
                {
                    "actionID": "sale_list_paging",
                    "actionType": "select",
                    "tableName": "LIST",
                    "parmsList": [
                        {"from": 0, "rows": 1, "sort_by": "DATADE", "sale_outside_yn": "N"}
                    ],
                },
            ],
        }

        self.__image_formats = ("image/png", "image/jpeg", "image/jpg")

    # Credential Manager로부터 받은 Authorized Header 정보를 저장
    def set_request_headers(self, header_dic):
        self.__request_headers = header_dic
        return self.__request_headers

    # 데이터 저장 시 각 API 요청에서 사용될 Request Body 저장
    def set_payload_sale(self, sale_no):
        self.__payload_sale = {
            "baseParms": {"sale_no": sale_no},
            "actionList": [{"actionID": "sale_info", "actionType": "select", "tableName": "SALE"}],
        }
        return self.__payload_sale

    def set_payload_lots(self, sale_no, lot_no):
        self.__payload_lots = {
            "baseParms": {"sale_no": sale_no, "lot_no": lot_no},
            "actionList": [
                {"actionID": "lot_info", "actionType": "select", "tableName": "LOT"},
                {"actionID": "lot_images", "actionType": "select", "tableName": "IMAGES"},
            ],
        }
        return self.__payload_lots

    # 서버 조회 후 종료된 경매 중 가장 최신의 경매 번호 받아오기
    def get_latest_sale_no(self):
        latest_sale_response = requests.post(
            self.__api_url, headers=self.__request_headers, json=self.__payload_latest_sale
        )
        latest_sale_response_json = json.loads(latest_sale_response.text)["tables"]["LIST"]["rows"]

        return int(latest_sale_response_json[0].get("SALE_NO"))

    # 로컬에 저장된 경매 정보 중 최신본 받아오기
    def get_local_latest_sale_no(self):
        data_path = os.path.join(os.path.dirname(__file__), "../resources/data/seoulauction/")

        sale_list = os.listdir(data_path)
        if sale_list:
            return max([int(files.split(".")[0].split("_")[1]) for files in sale_list])
        else:
            return 0

    # 새로 API를 통해 받아와야 할 경매 정보 return
    def check_sync_status(self):
        return {"local": self.get_local_latest_sale_no(), "latest": self.get_latest_sale_no()}

    # 해당 경매 번호의 경매 정보 받아오기
    def get_sale_data(self, sale_no):
        self.set_payload_sale(sale_no=sale_no)

        sale_response = requests.post(
            self.__api_url, headers=self.__request_headers, json=self.__payload_sale
        )
        sale_json = json.loads(sale_response.text)["tables"]["SALE"]["rows"]

        return sale_json if sale_json else None

    # 경매의 Lot 정보 받아오기
    def get_lot_data(self, sale_no, lot_no):
        self.set_payload_lots(sale_no=sale_no, lot_no=lot_no)

        lot_response = requests.post(
            self.__api_url, headers=self.__request_headers, json=self.__payload_lots
        )
        lot_json = json.loads(lot_response.text)["tables"]

        lot_info_json = lot_json["LOT"]["rows"]
        img_info_json = lot_json["IMAGES"]["rows"]

        return (lot_info_json, img_info_json)

    # 받아온 경매 정보와 Lot 정보를 이용해 Json 저장
    def save_sales_data(self, sale_no):

        sales_dic = {"sales": {}, "lots": [], "images": []}

        sales_info = self.get_sale_data(sale_no=sale_no)
        if not sales_info:
            print("해당 경매가 존재하지 않습니다.")
            return
        sales_dic["sales"] = sales_info[0]

        lot_no = 1  # 1번 Lot부터 시작하지 않는 경매가 있으려나..?
        if not bool(self.get_lot_data(sale_no, lot_no)[0]):
            print("경매는 존재하나 lot이 존재하지 않습니다.")
            return

        while lot_no > 0:
            (lot_info_json, img_info_json) = self.get_lot_data(sale_no, lot_no)

            sales_dic["lots"].append(lot_info_json[0])
            sales_dic["images"] = sales_dic["images"] + img_info_json

            lot_no = lot_info_json[0]["NEXT_LOT_NO"]

        json_save_path = os.path.join(
            os.path.dirname(__file__),
            "../" + self.__save_path_data + "sale_" + str(sale_no) + ".json",
        )

        with open(json_save_path, "w", encoding="utf-8") as json_file:
            json.dump(sales_dic, json_file, indent=4, ensure_ascii=False)

        return sales_dic

    # 이미지 주소를 받아 이를 파일로 저장 (로컬에 저장되는 경로는 서버와 동일)
    def save_single_lot_image(self, image_path, image_name):
        target_url = self.__img_url + image_path + "/" + image_name
        res = requests.get(target_url)

        image_headers = res.headers
        image_data = res.content

        # check image validity
        if not image_headers["content-type"] in self.__image_formats:
            return None
        else:
            absolute_save_path = os.path.join(
                os.path.dirname(__file__), "../" + self.__save_path_image
            )

            # make directory
            os.makedirs(absolute_save_path + image_path, exist_ok=True)
            # save image
            with open(absolute_save_path + image_path + "/" + image_name, "wb") as handler:
                handler.write(image_data)

            return absolute_save_path + image_path + "/" + image_name

    # run after sale data json file has been created
    # 경매 내 Lot 이미지들 모두 저장. 각 이미지 저장 사이 1~5초 중 랜덤한 시간동안 휴식 후 진행
    def save_sale_images(self, sale_no):
        sales_filename = os.path.join(
            os.path.dirname(__file__),
            "../" + self.__save_path_data + "sale_" + str(sale_no) + ".json",
        )

        if not os.path.exists(sales_filename):
            return None
        else:
            with open(sales_filename, "r", encoding="utf8") as f:
                f = json.load(f)
                lots_info = f["lots"]

            for lots in lots_info:
                if lots["LOT_IMG_PATH"] and lots["LOT_IMG_NAME"]:
                    self.save_single_lot_image(lots["LOT_IMG_PATH"], lots["LOT_IMG_NAME"])

                # rest for some seconds between image requests
                rand_value = random.uniform(1, self.__sleep_time)
                time.sleep(rand_value)

            return sale_no


if __name__ == "__main__":

    ##############################################################
    # 로그인, Authorized Header 생성 후 Crawler 객체에 Setting

    credential_manager = CredentialManager()
    auth_headers = credential_manager.get_authorized_header("seoulauction")

    seoulauction_crawler = SeoulAuctionDataCrawler()
    seoulauction_crawler.set_request_headers(auth_headers)

    ##############################################################
    # 새로 API를 통해 받아와야 할 경매 정보 return

    print(seoulauction_crawler.check_sync_status())

    ##############################################################
    # 경매 정보와 Lot 정보, 이미지 정보를 저장

    print(seoulauction_crawler.save_sales_data(688))
    print(seoulauction_crawler.save_sale_images(688))
