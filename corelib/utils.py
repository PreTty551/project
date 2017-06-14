import datetime
import random
import arrow
import json
import psutil

from django.conf import settings


def random_str(num=10):
    num_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    now_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = "".join(random.sample(num_list, num))
    return "%s%s" % (now_str, random_str)


def dict_to_xml(arr):
    """ dict转xml """
    xml = ["<xml>"]
    for k, v in arr.items():
        if v.isdigit():
            xml.append("<{0}>{1}</{0}>".format(k, v))
        else:
            xml.append("<{0}><![CDATA[{1}]]></{0}>".format(k, v))
    xml.append("</xml>")
    return "".join(xml)


def natural_time(localtime):
    if localtime:
        return arrow.get(localtime).humanize(locale='zh_CN')
    return ''


def send_msg_to_dingding(msg_info, access_token):
    payload = json.dumps({"msgtype": "text", "text": {"content": "%s" % msg_info}})
    p1 = psutil.Popen(["curl", "-X", "POST", "-H", "Content-Type: application/json", "--data", payload,
                      "https://oapi.dingtalk.com/robot/send?access_token=%s" % access_token])
    p1.communicate()


def avatar_url(avatar):
    if ".jpg" in avatar:
        return "%s/%s@base@tag=imgScale&w=150&h=150" % (settings.AVATAR_BASE_URL, avatar)
    else:
        return "http://img.gouhuoapp.com/%s?imageView2/1/w/150/h/150/format/jpg/q/80" % avatar
