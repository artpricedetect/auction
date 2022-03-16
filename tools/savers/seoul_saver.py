from fileinput import filename
from locale import currency
import requests
import os
import sys
import json
import logging
from datetime import datetime
import time

from webapp.models.work import Work
from webapp.models.worksize import WorkSize
from webapp.models.lot import Lot
from webapp.models.sale import Sale
from webapp.models.sale_details import SaleDetails
from webapp.models.artist import Artist
from webapp.models.organization import Organization

logger = logging.getLogger("my")


class SeoulSaver:
    # 인자로 받은 sale no 에 대한 경로 등 초기설정, sale_no는 string
    def __init__(self, sale_no):
        # 프로젝트의 루트 디렉토리 (= resources 전까지의 디렉토리)
        root_dir = os.path.dirname(
            os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
        )
        tail_dir = "/resources/data/seoulauction"
        total_dir = root_dir + tail_dir
        self.__jsonPath = os.path.join(total_dir, "sale_" + sale_no + ".json")

    # json 파일 경로를 전달해주는 함수
    def get_json_path(self):
        return self.__jsonPath

    # json 파일 경로를 인자로 받아 json 데이터를 리턴하는 함수
    def get_json_data(self):
        json_path = self.get_json_path()
        with open(json_path) as seoul_json:
            json_data = json.load(seoul_json)
        return json_data

    # work 객체 생성해서 반환해주는 함수
    def make_work_model(self, json_data):
        lots_data = json_data["lots"]
        # work_list = []
        # work_created_list = []
        for ld in lots_data:
            title_kor = ld["TITLE_KO_TXT"]
            title_eng = ld["TITLE_EN_TXT"]
            artist, artist_created = Artist.objects.get_or_create(
                name_kor=ld["ARTIST_NAME_KO_TXT"],
                name_eng=ld["ARTIST_NAME_EN_TXT"],
                born_year=ld["BORN_YEAR"],
            )  # , death_year=ld["DEATH_YEAR"])
            make_year = ld["MAKE_YEAR_KO"]
            edition_num = ld["EDITION"]
            material_kor = ld["MATE_NM"]
            material_eng = ld["MATE_NM_EN"]
            exhibition = json.dumps(ld["EXHI_INFO_JSON"])
            if ld["FRAME_CD"] == "framed":
                frame_yn = True
            elif ld["FRAME_CD"] == "unframed":
                frame_yn = False
            else:
                frame_yn = None
            # sign 정보가 json으로 되어있고, ko,en,cn 저장 이지만 거의 비어있음 추후 로직으로 해결
            # sign_yn = ld["SIGN_INFO_JSON"]
            # 데이터 까보면서 확인해야할듯
            status = ld["STAT_CD"]
            if ld["GUARANTEE_YN"] == "Y":
                guarantee_yn = True
            elif ld["GUARANTEE_YN"] == "N":
                guarantee_yn = False
            else:
                guarantee_yn = None
            img_url = ld["LOT_IMG_PATH"]

            work, work_created = Work.objects.get_or_create(
                title_kor=title_kor,
                title_eng=title_eng,
                artist_id=artist,
                make_year=make_year,
                edition_num=edition_num,
                material_kor=material_kor,
                material_eng=material_eng,
                exhibition=exhibition,
                frame_yn=frame_yn,
                status=status,
                guarantee_yn=guarantee_yn,
                img_url=img_url,
            )
            # work가 생성된 경우에만 work_list에 추가
            if work_created:
                for i in range(len(ld["LOT_SIZE_JSON"])):
                    size_ld = ld["LOT_SIZE_JSON"][i]
                    unit_id = size_ld["UNIT_CD"]
                    size_no = i
                    size1 = size_ld["SIZE1"]
                    size2 = size_ld["SIZE2"]
                    size3 = size_ld["SIZE3"]
                    if size_ld["CANVAS"] == 0:
                        canvas = None
                    else:
                        canvas = size_ld["CANVAS"]
                    # canvas = sizeLd["CANVAS"]
                    if size_ld["DIAMETER_YN"] == "Y":
                        diam_yn = True
                    elif size_ld["DIAMETER_YN"] == "N":
                        diam_yn = False
                    else:
                        diam_yn = None
                    # diam_yn = sizeLd["DIAMETER_YN"]
                    prefix = size_ld["PREFIX"]
                    suffix = size_ld["SUFFIX"]
                    mix_code = size_ld["MIX_CD"]
                    if size_ld["CANVAS_EXT_YN"] == "Y":
                        canvas_ext_yn = True
                    elif size_ld["CANVAS_EXT_YN"] == "N":
                        canvas_ext_yn = False
                    else:
                        canvas_ext_yn = None
                    work_size = WorkSize(
                        work_id=work,
                        unit_id=unit_id,
                        size_no=size_no,
                        size1=size1,
                        size2=size2,
                        size3=size3,
                        canvas=canvas,
                        diam_yn=diam_yn,
                        prefix=prefix,
                        suffix=suffix,
                        mix_code=mix_code,
                        canvas_ext_yn=canvas_ext_yn,
                    )
                    work_size.save()
        return

    # worksize:work n:1 로 bulk create 대신 save 구현

    # def make_worksize_model(self, json_data, work_list, work_created_list):
    #     lots_data = json_data["lots"]
    #     work_size_list = []
    #     count = 0

    #     for i in range(len(lots_data)):
    #         # work가 create된 경우에만 size list append
    #         # lots_data의 길이 = work_created_list의 길이
    #         if work_created_list[i]:
    #             # size가 여러개인 경우..?
    #             sizeLd = lots_data[i]["LOT_SIZE_JSON"][0]

    #             unit_id = sizeLd["UNIT_CD"]
    #             size1 = sizeLd["SIZE1"]
    #             size2 = sizeLd["SIZE2"]
    #             size3 = sizeLd["SIZE3"]

    #             # canvas_yn = sizeLd["CANVAS"]
    #             # diam_yn = sizeLd["DIAMETER_YN"]
    #             prefix = sizeLd["PREFIX"]
    #             suffix = sizeLd["SUFFIX"]
    #             mix_code = sizeLd["MIX_CD"]
    #             canvas_ext_yn = sizeLd["CANVAS_EXT_YN"]
    #             work_size = WorkSize(
    #                 work_id=work_list[count],
    #                 unit_id=unit_id,
    #                 size1=size1,
    #                 size2=size2,
    #                 size3=size3,
    #                 canvas_yn=canvas_yn,
    #                 diam_yn=diam_yn,
    #                 prefix=prefix,
    #                 suffix=suffix,
    #                 mix_code=mix_code,
    #                 canvas_ext_yn=canvas_ext_yn,
    #             )
    #             work_size_list.append(work_size)
    #             count += 1
    #     return work_size_list

    def make_lot_model(self, json_data, sale):
        lots_data = json_data["lots"]
        lot_list = []
        for ld in lots_data:
            lot_num = ld["LOT_NO"]
            if ld["SOLD_YN"] == "Y":
                sold_yn = True
            elif ld["SOLD_YN"] == "N":
                sold_yn = False
            else:
                sold_yn = None
            # sold_yn = ld["SOLD_YN"]
            sold_price = ld["LAST_PRICE"]
            start_price = ld["START_PRICE"]
            est_upper_price = ld["EXPE_PRICE_TO_JSON"]
            est_lower_price = ld["EXPE_PRICE_FROM_JSON"]
            bid_cnt = ld["BID_CNT"]

            lot = Lot(
                sale_id=sale,
                lot_num=lot_num,
                sold_yn=sold_yn,
                sold_price=sold_price,
                start_price=start_price,
                est_upper_price=est_upper_price,
                est_lower_price=est_lower_price,
                bid_cnt=bid_cnt,
            )
            lot_list.append(lot)
        return lot_list

    def make_sale_model(self, json_data):
        sale_data = json_data["sales"]
        org_id = Organization(id=1, name="SeoulAuction")
        internal_id = sale_data["SALE_NO"]
        name_kor = sale_data["SALE_TITLE_KO"]
        name_eng = sale_data["SALE_TITLE_EN"]
        type = sale_data["SALE_KIND_CD"]

        try:
            location_kor = sale_data["PLACE_JSON"]["ko"]
            location_eng = sale_data["PLACE_JSON"]["en"]
        except KeyError:
            location_kor = ""
            location_eng = ""

        start_dt = datetime.fromtimestamp(sale_data["FROM_DT"] / 1000)
        end_dt = datetime.fromtimestamp(sale_data["TO_DT"] / 1000)
        finished_dt = datetime.fromtimestamp(sale_data["END_DT"] / 1000)
        if sale_data["LIVE_BID_YN"] == "Y":
            is_livebid = True
        elif sale_data["LIVE_BID_YN"] == "N":
            is_livebid = False
        else:
            is_livebid = None
        currency = sale_data["CURR_CD"]

        sale = Sale(
            org_id=org_id,
            internal_id=internal_id,
            name_kor=name_kor,
            name_eng=name_eng,
            type=type,
            start_dt=start_dt,
            end_dt=end_dt,
            finished_dt=finished_dt,
            location_eng=location_eng,
            location_kor=location_kor,
            currency=currency,
            is_livebid=is_livebid,
        )
        return sale

    def make_sale_details_model(self, json_data, sale):
        lots_data = json_data["lots"]
        lot_count = len(lots_data)
        estimate_high = json_data["sales"]["MAX_KRW_EXPE_PRICE"]
        estimate_low = json_data["sales"]["MIN_KRW_EXPE_PRICE"]
        # todo: 로직으로 구현하는 column

        saleDetails = SaleDetails(
            id=sale,
            lot_count=lot_count,
            estimate_high=estimate_high,
            estimate_low=estimate_low,
        )
        return saleDetails


if __name__ == "__main__":
    # filename = os.path.join(os.path.dirname(__file__), "SeoulAuction_687.json")

    seoul_saver = SeoulSaver("688")
    # workList, workSizeList = seoul_saver.make_work_model()

    # print(jsonData["lots"][3]["EXHI_INFO_JSON"])
    json_data = seoul_saver.get_json_data()
    # salesData = jsonData["sales"]
    from_date = json_data["sales"]["FROM_DT"]
    print(from_date / 1000)
    print(datetime.fromtimestamp(from_date / 1000))
    # print(lotsData[0]["EXPE_PRICE_FROM_JSON"])
    # imagesData = jsonData["images"]
    # print(lotsData[0].keys())
    # for ld in lotsData:
    # print(ld["TITLE_KO_TXT"])
    # print(ld["TITLE_EN_TXT"])

    # with open(json_path) as seoulJson:
    #     seoulData = json.load(seoulJson)

    # print(seoulData)
