import time
import requests

from ks3.connection import Connection

from django.conf import settings


class KS3(object):

    def __init__(self, bucket_name="ida-avatar"):
        self.client = Connection(settings.KS3_KEY, settings.KS3_SECRET, host="ks3-cn-beijing.ksyun.com")
        self.bucket = self.client.get_bucket("ida-avatar")

    def fetch(self, url, filename=None, headers={"Content-Type": "image/jpeg"}):
        content = requests.get(url).content
        obj = self.bucket.new_key(filename)
        return obj.set_contents_from_string(content, headers=headers, policy="public-read")

    def fetch_avatar(self, url, user_id):
        filename = "%s_%s.jpg" % (user_id, int(time.time() * 1000))
        self.fetch(url=url, filename=filename)
        return filename
