import requests
import yaml
import os
import sys

import logging

logger = logging.getLogger("my")


class AlarmManager:
    def __init__(self):
        # Alarm Property 파일 세팅
        filename = os.path.join(os.path.dirname(__file__), "alarmProperties.yaml")

        with open(filename) as alarmManagerFile:
            alarmManager = yaml.load(alarmManagerFile, Loader=yaml.FullLoader)
            self.__maxIteration = alarmManager.get("maxIteration")
            self.__telegramToken = alarmManager.get("telegramToken")
            self.__telegramUserIds = alarmManager.get("telegramUserIds")

    def alarm(self, result):
        # print("Slack or Kakao")
        self.__telegramAlarm("Error : " + result)

    def __telegramAlarm(self, message):
        print("Telegram Bot Alarm")

        rootUrl = "https://api.telegram.org/bot" + self.__telegramToken
        serviceUrl = rootUrl + "/sendmessage?text=" + message

        for userId in self.__telegramUserIds:
            response = requests.post(serviceUrl + "&&chat_id=" + str(userId))
            print(response)

    # check user Token https://api.telegram.org/bot5207445639:AAHBx_-eFlU1sP3XWD-mP1eAEf6oNNI3XTQ/getUpdates


if __name__ == "__main__":
    test = AlarmManager()
    test.alarm("hello")
