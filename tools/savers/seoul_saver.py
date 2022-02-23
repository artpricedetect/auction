from fileinput import filename
import requests
import yaml
import os
import sys
import json

import logging

logger = logging.getLogger("my")


class SeoulSaver:
    def __init__(self):
        # Saver Property 파일 세팅
        filename = os.path.join(os.path.dirname(__file__), "saver_properties.yaml")

        with open(filename) as seoulSaverManagerFile:
            __saver_info = yaml.load(seoulSaverManagerFile, Loader=yaml.FullLoader).get(
                "seoulauction"
            )
            self.__json_file_path = __saver_info.get("json_file_path")

    # properties yaml에서 json 파일 경로를 전달해주는 함수
    def get_json_path(self):
        return self.__json_file_path

    # json 파일 경로를 인자로 받아 json 데이터를 리턴하는 함수
    def get_json_data(self):
        json_path = self.get_json_path()
        with open(json_path) as seoulJson:
            jsonData = json.load(seoulJson)
        return jsonData


if __name__ == "__main__":
    filename = os.path.join(os.path.dirname(__file__), "SeoulAuction_687.json")

    seoul_saver = SeoulSaver()
    jsonData = seoul_saver.get_json_data()
    salesData = jsonData["sales"]
    lotsData = jsonData["lots"]
    imagesData = jsonData["images"]
    print(lotsData[0].keys())
    # for ld in lotsData:
        # print(ld["TITLE_KO_TXT"])
        # print(ld["TITLE_EN_TXT"])

    # with open(json_path) as seoulJson:
    #     seoulData = json.load(seoulJson)

    # print(seoulData)
