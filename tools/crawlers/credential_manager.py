import requests
import yaml
import os
from bs4 import BeautifulSoup as bs
import re
import json


class CredentialManager:
    def __init__(self):
        # Property 파일 세팅
        filename = os.path.join(os.path.dirname(__file__), "crawler_properties.yaml")
        with open(filename) as crawler_properties_file:
            self.__credintial_info = yaml.load(crawler_properties_file, Loader=yaml.FullLoader)

    def get_authorized_header(self, organization):
        if organization == "seoulauction":
            authorized_header = self.__get_seoulauction_login_session()
            return authorized_header if authorized_header else None

        if organization == 'kauction':
            authorized_header = self.__get_kauction_login_session()
            return authorized_header if authorized_header else None

    def __get_kauction_login_session(self):
        credintials = self.__credintial_info.get("kauction")
        url = credintials['login_url']
        headers = {'content-type': 'application/json'}
        data = json.dumps(
            {"id": credintials['id'], "pwd": credintials['password'], "is_saved": "F", "highlight_read": ""})

        req = requests.post(url, headers=headers, data=data)

        if req.json():
            if req.json()['code'] == '00':
                return req.cookies.get_dict()
            else:  # 수정 필요
                print('login_fail')  # 수정 필요
        return None

    def __get_seoulauction_login_session(self):

        # get unauthorized csrf token & session id
        credintials = self.__credintial_info.get("seoulauction")

        s = requests.Session()
        login_html = s.get(credintials.get("entrypoint_url")).text
        login_soup = bs(login_html, "html.parser")
        unauthorized_csrf = login_soup.find("input", {"name": "_csrf"}).get("value")

        # log in using unauthorized csrf token, id, password
        login_data = {
            "loginId": credintials.get("id"),
            "password": credintials.get("password"),
            "_csrf": unauthorized_csrf,
        }

        login_response = s.post(credintials.get("login_url"), data=login_data)

        if login_response.status_code == 200:

            # retrieve authorized csrf token, session id
            authorized_csrf = (
                re.search(r"'_csrf', '[^)]+", login_response.text).group(0).split("'")[3]
            )
            authorized_session_id = s.cookies.get_dict().get("JSESSIONID")

            return {
                "X-CSRF-TOKEN": authorized_csrf,
                "Cookie": "JSESSIONID=" + authorized_session_id,
            }

        else:
            return None


if __name__ == "__main__":
    print("logging in to SeoulAuction...")
    login_info = CredentialManager().get_authorized_header("seoulauction")

    if login_info:
        print("log in success!")
        print(login_info)
    else:
        print("log in failed")
