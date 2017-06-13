# -*- coding: utf-8 -*-
import datetime

from django.db import models
from user.models.user import User

class Report(models.Model):
	user_id = models.IntegerField()
	date = models.DateTimeField(auto_now_add=True)


	@classmethod
	def report(request):
		if request.method == 'GET':
			user_id = request.GET.get('id')
			user_reported_id = request.GET.get('uid')
			result = disable_login()
			return result


class LogReport(models.Model):
	user_id = models.IntegerField()
	user_reported_id = models.IntegerField()
	date = models.DateTimeField(auto_now_add=True)

