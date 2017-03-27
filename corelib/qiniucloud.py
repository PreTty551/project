# -*- coding: utf-8 -*-
import datetime
import random

from django.conf import settings

from qiniu import Auth, BucketManager, put_data


class Qiniu(object):

    def __init__(self):
        self.auth = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)

    def upload_avatar(self, img_stream):
        photo_name = self.random_photo_name()
        token = self.auth.upload_token("gouhuo")
        ret, info = put_data(token, photo_name, img_stream)
        return ret, photo_name

    def upload_image(self, img_stream):
        photo_name = self.random_photo_name()
        token = self.auth.upload_token("gouhuo")
        ret, info = put_data(token, photo_name, img_stream)
        return ret, photo_name

    def random_photo_name(self):
        num_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        now_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        random_number = "".join(random.sample(num_list, 6))
        return "%s%s" % (now_str, random_number)

    def fetch(self, url, bucket="gouhuo"):
        """将远程图片上传到七牛, 返回存储的文件名"""
        bucket_manager = BucketManager(self.auth)
        res, info = bucket_manager.fetch(url=url,
                                         bucket=bucket,
                                         key=self.random_photo_name())
        return res.get("key")
