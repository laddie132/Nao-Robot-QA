#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Han"
__email__ = "liuhan132@foxmail.com"

import sys
import time
import logging
import paramiko
from utils import sftp_get
from remote_service import MRCService, ASRService

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

QuestionAnswer = None
memory = None


class NaoRobot:
    username = 'nao'
    password = 'nao'

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def connect(self):
        # We need this broker to be able to construct
        # NAOqi modules and subscribe to other modules
        # The broker must stay alive until the program exists
        self.myBroker = ALBroker("myBroker",
                                 "0.0.0.0",     # listen to anyone
                                 0,             # find a free port and use it
                                 self.ip,       # parent broker IP
                                 self.port)     # parent broker port

    def run(self, context):
        # Warning: QuestionAnswer must be a global variable
        # The name given to the constructor must be the name of the
        # variable
        global QuestionAnswer
        QuestionAnswer = QAModule("QuestionAnswer", self.ip, context)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Interrupted by user, shutting down")
            self.myBroker.shutdown()
            sys.exit(0)


class QAModule(ALModule):
    tmp_audio_path = '/tmp/tmp_record.wav'

    def __init__(self, name, ip, context, rate=8000, channels=(0, 0, 1, 0)):
        ALModule.__init__(self, name)
        self.ip = ip
        self.context = context
        self.rate = rate
        self.channels = channels  # [left, right, front, rear]

        self.asr_service = ASRService()
        self.regist_modules()

    def regist_modules(self):
        self.asp = ALProxy("ALAnimatedSpeech")
        self.record = ALProxy("ALAudioRecorder")
        self.configuration = {"bodyLanguageMode": "contextual"}

        self.asp.say('你好！', self.configuration)

        # Subscribe to the SoundDetected event:
        global memory
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("SoundDetected",
                                "QuestionAnswer",
                                "onSoundDetected")

    # todo: change the 8000 to 16000
    def onSoundDetected(self):
        memory.unsubscribeToEvent("SoundDetected",
                                  "QuestionAnswer")

        self.asp.say('你想知道什么？', self.configuration)

        logging.info('Recording...')
        self.record.startMicrophonesRecording(self.tmp_audio_path, 'wav', self.rate, self.channles)
        time.sleep(8)
        self.record.stopMicrophonesRecording()
        logging.info('Record finished')

        logging.info('Downloading the audio from robot {}...'.format(self.ip))
        sftp_get(self.ip,
                 22,
                 NaoRobot.username,
                 NaoRobot.password,
                 self.tmp_audio_path,
                 self.tmp_audio_path)
        logging.info('Download finished')

        logging.info('Recognizing...')
        question = self.asr_service.recognize(self.tmp_audio_path, rate=self.rate)
        logging.info('Got the question: {}'.format(question))

        logging.info('Comprehending...')
        answer = MRCService.predict(self.context, question)
        logging.info('Got the answer: {}'.format(answer))

        if answer != '':
            self.asp.say(answer, self.configuration)
        else:
            self.asp.say('对不起，我不明白你在说什么。', self.configuration)

        # Subscribe again to the event
        memory.subscribeToEvent("SoundDetected",
                                "QuestionAnswer",
                                "onSoundDetected")
