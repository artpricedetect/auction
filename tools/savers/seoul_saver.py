from fileinput import filename
import requests
import yaml
import os
import sys
import json
import logging

from webapp.models.work import Work
from webapp.models.worksize import WorkSize
from webapp.models.lot import Lot
from webapp.models.sale import Sale
from webapp.models.sale_details import SaleDetails
from webapp.models.artist import Artist

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
    def make_work_model(self, jsonData):
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
    
    def make_worksize_model(self, jsonData, workList):
        lotsData = jsonData["lots"]
        workSizeList = []
        count = 0
        for ld in lotsData:
            sizeLd = ld["LOT_SIZE_JSON"][0]

            unit_id = sizeLd["UNIT_CD"]
            size1 = sizeLd["SIZE1"]
            size2 = sizeLd["SIZE2"]
            size3 = sizeLd["SIZE3"]
            canvas_yn = sizeLd["CANVAS"]
            diam_yn = sizeLd["DIAMETER_YN"]
            prefix = sizeLd["PREFIX"]
            suffix = sizeLd["SUFFIX"]
            mix_code = sizeLd["MIX_CD"]
            canvas_ext_yn = sizeLd["CANVAS_EXT_YN"]

            workSize = WorkSize(work_id=workList[count], unit_id=unit_id, size1=size1, size2=size2, size3=size3, canvas_yn=canvas_yn, diam_yn=diam_yn, prefix=prefix, suffix=suffix, mix_code=mix_code, canvas_ext_yn=canvas_ext_yn)
            workSizeList.append(workSize)
            count += 1
        return workSizeList

    def make_lot_model(self, jsonData):
        lotsData = jsonData["lots"]
        lotList = []
        for ld in lotsData:
            sale_id = ld["SALE_NO"]
            lot_num = ld["LOT_NO"]
            sold_yn = ld["SOLD_YN"]
            sold_price = ld["LAST_PRICE"]
            start_price = ld["START_PRICE"]
            est_upper_price = ld["EXPE_PRICE_TO_JSON"]
            est_lower_price = ld["EXPE_PRICE_FROM_JSON"]
            bid_cnt = ld["BID_CNT"]

            lot = Lot(sale_id=sale_id, lot_num=lot_num, sold_yn=sold_yn, sold_price=sold_price, start_price=start_price, est_upper_price=est_upper_price, est_lower_price=est_lower_price, bid_cnt=bid_cnt)
            lotList.append(lot)
        return lotList
    
    def make_sale_model(self, jsonData):
        sale = Sale()
        return sale
    
    def make_sale_details_model(self, jsonData):
        saleDetailsList = []
        return saleDetailsList
    
    def make_artist_model(self, jsonData):
        artistList = []
        return artistList



if __name__ == "__main__":
    # filename = os.path.join(os.path.dirname(__file__), "SeoulAuction_687.json")

    seoul_saver = SeoulSaver("688")
    # workList, workSizeList = seoul_saver.make_work_model()

    # print(jsonData["lots"][3]["EXHI_INFO_JSON"])
    jsonData = seoul_saver.get_json_data()
    # salesData = jsonData["sales"]
    lotsData = jsonData["lots"]
    print(jsonData["sales"])
    # print(lotsData[0]["EXPE_PRICE_FROM_JSON"])
    # imagesData = jsonData["images"]
    # print(lotsData[0].keys())
    # for ld in lotsData:
        # print(ld["TITLE_KO_TXT"])
        # print(ld["TITLE_EN_TXT"])

    # with open(json_path) as seoulJson:
    #     seoulData = json.load(seoulJson)

    # print(seoulData)
