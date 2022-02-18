import requests
import json
import yaml
import os

from credential_manager import CredentialManager


class SeoulAuctionDataCrawler:
    def __init__(self):
        # Property 파일 세팅
        filename = os.path.join(os.path.dirname(__file__), "crawler_properties.yaml")

        with open(filename) as crawler_properties_file:
            self.__api_url = (
                yaml.load(crawler_properties_file, Loader=yaml.FullLoader)
                .get("seoulauction")
                .get("api_url")
            )

        self.__request_headers = None
        self.__payload_sale = None
        self.__payload_lots = None

    def get_api_url(self):
        return self.__api_url

    def set_request_headers(self, header_dic):
        self.__request_headers = header_dic
        return self.__request_headers

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

    def get_sale_data(self, sale_no):
        self.set_payload_sale(sale_no=sale_no)

        sale_response = requests.post(
            self.__api_url, headers=self.__request_headers, json=self.__payload_sale
        )
        sale_json = json.loads(sale_response.text)["tables"]["SALE"]["rows"]

        return sale_json if sale_json else None

    def get_lot_data(self, sale_no, lot_no):
        self.set_payload_lots(sale_no=sale_no, lot_no=lot_no)

        lot_response = requests.post(
            self.__api_url, headers=self.__request_headers, json=self.__payload_lots
        )
        lot_json = json.loads(lot_response.text)["tables"]

        lot_info_json = lot_json["LOT"]["rows"]
        img_info_json = lot_json["IMAGES"]["rows"]

        return (lot_info_json, img_info_json)

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
            "../resources/data/seoulauction/sale_" + str(sale_no) + ".json",
        )

        with open(json_save_path, "w", encoding="utf-8") as json_file:
            json.dump(sales_dic, json_file, indent=4, ensure_ascii=False)

        return sales_dic


if __name__ == "__main__":

    credential_manager = CredentialManager()
    auth_headers = credential_manager.get_authorized_header("seoulauction")

    seoulauction_crawler = SeoulAuctionDataCrawler()
    seoulauction_crawler.set_request_headers(auth_headers)

    print(seoulauction_crawler.save_sales_data(688))
