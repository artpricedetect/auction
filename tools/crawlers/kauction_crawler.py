import os
import requests
import pandas as pd
import yaml
import json

from tools.crawlers.credential_manager import CredentialManager


# 프로젝트에서는 한 번의 경매를 sale이라고 하지만, k-acution에서 제공하는 api주소, json 키 값등에서는 auc이라는 약어를 사용하므로
# 이 클래스에서는 파라미터 이름이나 변수 이름에서는 auc이라고 표기하고   (json 등으로 key-value 넘겨주는 과정에서 혼란 방지
# 함수 명은 sale로 표기함  (크롤러들이 같은 함수 이름을 가지도록)

class KAuctionCrawler:
    def __init__(self):
        filename = os.path.join(os.path.dirname(__file__), "crawler_properties.yaml")
        try:
            with open(filename) as crawler_properties_file:
                credential_info = yaml.load(crawler_properties_file, Loader=yaml.FullLoader)
                try:
                    self.__credentials = credential_info['kauction']
                except:
                    pass  # key가 없는경우
        except:
            pass  # 파일이 없는 경우

        # content-negotiation을 통해 lot정보의 json 데이터를 한글/영어로 제공한다.
        # 영어로 제공할 때 값이 달라지는 데이터 column들을 담고 있다.
        self.__en_col = ['artist_name', 'title', 'size', 'material', 'display_price_max', 'auc_title', 'card_message']
        self.__org = 'kauction'
        self.__cookie = CredentialManager().get_authorized_header(self.__org)
        self.__auc_kind_dict = {'Major': '1', 'Premium': '2', 'Weekly': '4'}
        self.__auc_kind_code_dict = {'1': 'Major', '2': 'Premium', '4': 'Weekly'}
        self.__image_path_dict = {'Major': 'Work/', 'Premium': 'Kmall/Work/', 'Weekly': 'Konline/Work/'}
        self.__image_size_dict = {'Major': {'L': ('', ''), 'M': ('T/', '_L'), 'S': ('T/', '')},
                                  'Premium': {'L': ('', '_L'), 'M': ('', '_L'), 'S': ('', '')},
                                  'Weekly': {'L': ('', '_L'), 'M': ('', '_L'), 'S': ('', '')}}

    def get_latest_sale_no(self):
        url_base = self.__credentials['auction_url']
        req_data = json.dumps({"search": "", "page": "1", "sort_column": "auc_end_date", "sort_option": "DESC"})
        headers = {'cookie': self.__cookie, 'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                   'Content-Type': 'application/json'}

        latest_dict = {}
        for ak in self.__auc_kind_dict.keys():
            url = url_base + ak
            try:
                req = requests.post(url, headers=headers, data=req_data)
                try:
                    latest_num = req.json()['data'][0]['auc_num']
                    latest_dict[ak] = latest_num
                except:
                    status_code = req.status_code  # 코드 보여주면 200인데 잘 안온건지 ,400번대라서 안온건지 알 수 있음
                    pass  # data가 잘 안온경우
            except:
                pass  # 네트워크오류
        return latest_dict

    def get_sale_data(self, auc_kind, page=1):
        try:
            url = self.__credentials['auction_url'] + auc_kind
        except:
            pass  # auc_kind를 다른 형식으로 넣는 경우

        req_data = json.dumps({"search": "", "page": "1", "sort_column": "auc_end_date", "sort_option": "DESC"})
        headers = {'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                   'Content-Type': 'application/json'} | self.__cookie
        try:
            req = requests.post(url, headers=headers, data=req_data)
            try:
                auc_data = req.json()['data']
            except:
                pass
        except:
            pass
        return auc_data

    def get_lot_data(self, auc_num, auc_kind, page=1, page_size=3000):

        auc_kind_code = self.__auc_kind_code_dict[auc_kind]
        url = self.__credentials['lot_url'] + auc_kind_code + '/' + auc_num

        headers = {'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                   'Content-Type': 'application/json'} | self.__cookie
        headers_en = {'Content-Type': 'application/json'} | self.__cookie
        req_data = json.dumps(
            {"page": page, "page_size": page_size, "page_type": "P", "auc_kind": auc_kind_code, "auc_num": auc_num})


        req = requests.post(url, headers=headers, data=req_data)
        req_en = requests.post(url, headers=headers_en, data=req_data)

        data = req.json()['data']
        data_en = req_en.json()['data']

        data_merged = [dt | {k + '_en': v for k, v in dte if k in self.__en_col} for dt, dte in zip(data, data_en)]
        # -------에러 처리 -------
        return data_merged

    def get_image_data(self, auc_num, auc_kind, image_name, size='M'):

        if auc_kind not in self.__image_path_dict:
            pass  # wrong parameter

        if type(image_name) == str and '.' in image_name:
            name, ext = image_name.split('.')
        else:
            pass  # wrong param
        pre, post = self.__image_size_dict[auc_kind][size]
        image_path = '0' * (4 - len(str(auc_num))) + str(auc_num) + '/' + pre + name + post + '.' + ext
        url = self.__credentials['image_url'] + self.__image_path_dict[auc_kind] + image_path
        headers = {} | self.__cookie
        print(url)
        req = requests.get(url, headers=headers)

        return req.content


# 가장 최근 회차가 몇 번인지 불러오기
# 경매 정보 불러오기
# 하나의 경매에 대한 랏 정보 불러오기
# 이미지 불러오기
if __name__ == "__main__":
    c = KAuctionCrawler()
    image = c.get_image_data('146', 'Major', 'M0146001001.jpg')
    print(image)
