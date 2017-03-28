import datetime
import random


def random_str(num=10):
    num_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    now_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = "".join(random.sample(num_list, num))
    return "%s%s" % (now_str, random_str)


def dict_to_xml(arr):
    """ dict转xml """
    xml = ["<xml>"]
    for k, v in arr.iteritems():
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
