import os
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings


def read_file():
	file = open(os.path.join(settings.BASE_DIR, 'tickers.txt'))
	resp = ''

	for index, row in file:
		resp += line
	file.close()
	
	return resp

def parser(request):
	return HttpResponse(read_file())
