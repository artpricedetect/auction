import os
import json
import datetime
import re
from webapp.models.sale import Sale
from webapp.models.sale_details import SaleDetails
from webapp.models.organization import Organization
from webapp.models.artist import Artist
from webapp.models.work import Work
from webapp.models.worksize import WorkSize
from webapp.models.lot import Lot


class KaucSaver:
    def __init__(self):
        self.aucs_json_data = None
        self.lots_json_data = None
        self.sale = None
        self.max_estimate_lot = 0
        self.min_estimate_lot = 999999999999

    # 추후 sale 번호 입력에 따라 수정 예정
    def get_json_data(self):
        dir_path = os.path.dirname(__file__)
        aucs_json_path = os.path.join(
            dir_path, "..", "..", "resources", "data", "kauction", "Major", "sale_146.json"
        )
        lots_json_path = os.path.join(
            dir_path, "..", "..", "resources", "data", "kauction", "Major", "lot_146.json"
        )

        self.aucs_json_data = json.load(open(aucs_json_path))
        self.lots_json_data = json.load(open(lots_json_path))

    @staticmethod
    def get_kauc_org():
        org, org_is_created = Organization.objects.get_or_create(name="KAuction")

        return org

    @staticmethod
    def str_to_datetime(date_str):
        # str 형식 = "YYYY-MM-DD HH:MM:SS"
        return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def char_to_boolean(bool_char):
        if bool_char == "y" or bool_char == "Y":
            return True
        elif bool_char == "n" or bool_char == "N":
            return False
        else:
            return None

    @staticmethod
    def trim_direct_date(direct_date):
        if direct_date:
            return (
                direct_date.replace("(추정)", "")
                .replace("조선말기", "")
                .replace("~", "")
                .replace("?", "")
                .replace("外", "")
                .replace("생몰년미상", "")
                .replace("생몰년 미상", "")
                .replace("미상", "")
                .replace(" 외", "")
                .strip()
            )
        else:
            return ""

    @staticmethod
    def get_birth_date_from_direct_date(direct_date):
        if "-" in direct_date:
            return direct_date.split("-")[0].strip()
        elif re.match("b.[0-9]{4}", direct_date):
            return re.match("b.[0-9]{4}", direct_date)[0][2:]
        else:
            return direct_date

    @staticmethod
    def get_death_date_from_direct_date(direct_date):
        if re.findall(" [a-zA-Z][a-zA-Z]", " " + direct_date):
            direct_date = (" " + direct_date)[
                : (" " + direct_date).index(re.findall(" [a-zA-Z][a-zA-Z]", " " + direct_date)[0])
            ].strip()

        if "b." in direct_date:
            return None
        elif "-" in direct_date:
            return direct_date.split("-")[1].strip()
        else:
            return None

    @staticmethod
    def get_nationality_from_direct_date(artist_name, direct_date):
        if re.findall(" [a-zA-Z][a-zA-Z]", " " + direct_date):
            return (" " + direct_date)[
                (" " + direct_date).index(re.findall(" [a-zA-Z][a-zA-Z]", " " + direct_date)[0]) :
            ].strip()
        elif not artist_name:
            return "Unknown"
        else:
            return "Korea Republic"

    def apply_estimated_price(self, estimated_low, estimated_high):
        self.min_estimate_lot = min(estimated_low, self.min_estimate_lot)
        self.max_estimate_lot = max(estimated_high, self.max_estimate_lot)

    def save_sale_data(self):
        type_lambda = lambda a: "1" if (a == "1") else "2"

        sale = Sale.objects.create(
            org_id=self.get_kauc_org(),
            internal_id=self.aucs_json_data["uid"],
            name_kor=self.aucs_json_data["auc_title_kr"],
            name_eng=self.aucs_json_data["auc_title_en"],
            type=type_lambda(self.aucs_json_data["auc_kind"]),
            location_kor=self.aucs_json_data["auc_place"],
            start_dt=self.str_to_datetime(self.aucs_json_data["auc_start_date"]),
            end_dt=self.str_to_datetime(self.aucs_json_data["auc_end_date"]),
            finished_dt=self.str_to_datetime(self.aucs_json_data["auc_bid_end_date"]),
            is_livebid=self.char_to_boolean(self.aucs_json_data["live_yn"]),
            currency="KRW",
        )

        self.sale = sale

    def save_artist_work_lot_data(self):
        name_kor_lambda = lambda a: "작자 미상" if not a else a
        name_eng_lambda = lambda a: "Unknown" if not a else a
        edition_lambda = lambda a: False if (a == "") else True
        sign_lambda = lambda a: True if ("sign" in a) else False
        frame_lambda = lambda a: True if (("frame" in a) and not ("unframe" in a)) else False
        guarantee_lambda = lambda a: True if ("certificate" in a) else False
        size_lambda = lambda a: "cm" if ("cm" in a) else "inch"

        for i in self.lots_json_data:
            try:
                artist = Artist.objects.get(kauc_uid=i["artist_uid"])
            except Artist.DoesNotExist:
                artist = Artist.objects.create(
                    name_kor=name_kor_lambda(i["artist_name"]),
                    name_eng=name_eng_lambda(i["artist_name_en"]),
                    born_year=self.get_birth_date_from_direct_date(
                        self.trim_direct_date(i["direct_date"])
                    ),
                    death_year=self.get_death_date_from_direct_date(
                        self.trim_direct_date(i["direct_date"])
                    ),
                    nationality=self.get_nationality_from_direct_date(
                        i["artist_name"], self.trim_direct_date(i["direct_date"])
                    ),
                    kauc_uid=i["artist_uid"],
                )

            try:
                work = Work.objects.get(
                    title_kor=i["title"], artist_id=artist, make_year=i["make_date"]
                )
            except Work.DoesNotExist:
                work = Work.objects.create(
                    title_kor=i["title"],
                    title_eng=i["title_en"],
                    artist_id=artist,
                    make_year=i["make_date"],
                    edition_yn=edition_lambda(i["edition"]),
                    edition_num=i["edition"],
                    material_kor=i["material"],
                    material_eng=i["material_en"],
                    kind=None,
                    exhibition=i["exhibition"],
                    frame_yn=frame_lambda(i["desc"].lower()),
                    sign_yn=sign_lambda(i["desc"].lower()),
                    status=i["condition"],
                    guarantee_yn=guarantee_lambda(i["desc"].lower()),
                    img_url=i["img_file_name"],
                )

                WorkSize.objects.create(
                    work_id=work,
                    size_no=1,
                    unit_id=size_lambda(i["size"]),
                    size1=i["size_length"],
                    size2=i["size_width"],
                    size3=None,
                    canvas_ext_yn=None,
                )

            Lot.objects.create(
                sale_id=self.sale,
                work_id=work,
                lot_num=i["lot_num"],
                sold_yn=None,
                start_price=i["price_start"],
                est_upper_price=i["price_estimated_high"],
                est_lower_price=i["price_estimated_low"],
                bid_cnt=None,
            )
            self.apply_estimated_price(i["price_estimated_low"], i["price_estimated_high"])

    def save_sale_details_data(self):
        SaleDetails.objects.create(
            id=self.sale,
            lot_count=self.aucs_json_data["work_count"],
            estimate_high=self.max_estimate_lot,
            estimate_low=self.min_estimate_lot,
        )
