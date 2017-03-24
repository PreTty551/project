# -*- coding: utf-8 -*-
import requests
import json

from django.conf import settings


class Weibo(object):
    API_HOST = "https://api.weibo.com"
    ACCESS_TOKEN_URL = "%s/oauth2/access_token" % API_HOST
    USER_INFO_URL = "%s/2/users/show.json?access_token=%s&uid=%s"

    def __init__(self, access_token="", uid=""):
        self.client_id = settings.WEIBO_CLIENT_KEY
        self.client_secret = settings.WEIBO_CLIENT_SECRET
        self.uid = uid
        self.access_token = access_token

    def fetch_access_token(self, code):
        url = self.ACCESS_TOKEN_URL
        headers = {"Content-Type": "application/json"}
        data = {"client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": ""}
        res = requests.post(url, headers=headers, data=json.dumps(data))
        obj = res.json() if res.text else {}
        self.uid = obj.get("uid", "")
        self.access_token = obj.get("access_token", "")

    def get_user_info(self):
        url = self.USER_INFO_URL % (self.API_HOST, self.access_token, self.uid)
        res = requests.get(url)
        obj = res.json() if res.text else {}
        if not hasattr(obj, "error"):
            return

        return {
            "uid": obj["id"],
            "nickname": obj["screen_name"],
            "avatar": obj["avatar_large"],
            "gender": 1 if obj["gender"] == "m" else 0
        }
