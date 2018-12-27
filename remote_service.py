#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Han"
__email__ = "liuhan132@foxmail.com"

import json
import logging
import requests
from aip import AipSpeech


class MRCService:
    url = 'http://10.108.211.36:9998/api/mrc'

    @staticmethod
    def predict(context, question):
        data = {'context': context, 'question': question}
        r = requests.post(MRCService.url, data)

        r_json = json.loads(r.text)
        answer = r_json['answer'].encode('utf-8')

        return answer


class ASRService:
    APP_ID = '15208225'
    API_KEY = 'pbNaCWWEzTNU2vC4BheNPSKd'
    SECRET_KEY = 'ynRXr99gKc2yV3mtXuZ5UTVLLEPZHySk'

    def __init__(self):
        self.client = AipSpeech(self.APP_ID, self.API_KEY, self.SECRET_KEY)

    @staticmethod
    def get_file_content(file_path):
        with open(file_path, 'rb') as fp:
            return fp.read()

    def recognize(self, file_path, format='wav', rate=8000, dev_pid=1537):
        r = self.client.asr(self.get_file_content(file_path), format, rate, {
            'dev_pid': dev_pid,
        })

        if r['err_no'] != 0:
            logging.error(r)
            return ''

        result = r['result']
        if len(result) > 0:
            logging.debug(result)

        return result[0]