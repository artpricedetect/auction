from fileinput import filename
import requests
import yaml
import os
import sys
import json
from webapp.models.work import Work
import logging

logger = logging.getLogger("my")


class SeoulSaver:
    # 인자로 받은 sale no 에 대한 경로 등 초기설정, sale_no는 string
    def __init__(self, sale_no):
        # 프로젝트의 루트 디렉토리 (= resources 전까지의 디렉토리)
        rootDir = os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))
        tailDir = "/resources/data/seoulauction"
        totalDir = rootDir + tailDir
        self.__jsonPath = os.path.join(totalDir, "sale_"+sale_no+".json")


    # json 파일 경로를 전달해주는 함수
    def get_json_path(self):
        return self.__jsonPath

    # json 파일 경로를 인자로 받아 json 데이터를 리턴하는 함수
    def get_json_data(self):
        json_path = self.get_json_path()
        with open(json_path) as seoulJson:
            jsonData = json.load(seoulJson)
        return jsonData
    
    # work 객체 생성해서 반환해주는 함수
    def make_work_model(self):
        jsonData = self.get_json_data()
        lotsData = jsonData["lots"]
        workList = []
        for ld in lotsData:
            title_kor = ld["TITLE_KO_TXT"]
            title_eng = ld["TITLE_EN_TXT"]
            make_year = ld["MAKE_YEAR_KO"]
            edition_num = ld["EDITION"]
            material_kor = ld["MATE_NM"]
            material_eng = ld["MATE_NM_EN"]
            exhibition = json.dumps(ld["EXHI_INFO_JSON"])
            frame_yn = ld["FRAME_CD"]
            # sign 정보가 json으로 되어있고, ko,en,cn 저장 이지만 거의 비어있음 추후 로직으로 해결
            # sign_yn = ld["SIGN_INFO_JSON"]
            
            # 데이터 까보면서 확인해야할듯
            status = ld["STAT_CD"]
            guarantee_yn = ld["GUARANTEE_YN"]
            img_url = ld["LOT_IMG_PATH"]

            work = Work(title_kor=title_kor, title_eng=title_eng, make_year=make_year, edition_num=edition_num, material_kor=material_kor, material_eng=material_eng, exhibition=exhibition, frame_yn=frame_yn, status=status, guarantee_yn=guarantee_yn, img_url=img_url)
            workList.append(work)
        return workList


if __name__ == "__main__":
    # filename = os.path.join(os.path.dirname(__file__), "SeoulAuction_687.json")

    seoul_saver = SeoulSaver("688")
    jsonData = seoul_saver.get_json_data()
    # print(jsonData["lots"][3]["EXHI_INFO_JSON"])
    # jsonData = seoul_saver.get_json_data()
    # salesData = jsonData["sales"]
    # lotsData = jsonData["lots"]
    # imagesData = jsonData["images"]
    # print(lotsData[0].keys())
    # for ld in lotsData:
        # print(ld["TITLE_KO_TXT"])
        # print(ld["TITLE_EN_TXT"])

    # with open(json_path) as seoulJson:
    #     seoulData = json.load(seoulJson)

    # print(seoulData)
