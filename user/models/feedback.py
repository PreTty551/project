from django.db import models
from django.conf import settings
from django.utils.translation import ugettext

from corelib.errors import BaseError, ErrorCodeField


class FeedBack(models.Model):
    user_id = models.IntegerField(db_index=True)
    content = models.TextField()
