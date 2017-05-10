import requests
from django.conf import settings


class Twilio(object):
    API_KEY = settings.TWILIO_API_KEY
    SEND_API = "https://api.authy.com/protected/json/phones/verification/start?api_key=%s" % API_KEY
    VALID_API = "https://api.authy.com/protected/json/phones/verification/check"

    @classmethod
    def send_sms(cls, mobile, country_code):
        data = {
            "phone_number": mobile,
            "country_code": country_code,
            "via": "sms"
        }
        res = requests.post(cls.SEND_API, data=data).json()
        if res["success"]:
            return True
        return False

    @classmethod
    def valid_sms(cls, mobile, country_code, code):
        data = {
            "api_key": cls.API_KEY,
            "phone_number": mobile,
            "country_code": country_code,
            "verification_code": code
        }
        res = requests.get(cls.VALID_API, data=data).json()
        if res["success"]:
            return True
        return False
