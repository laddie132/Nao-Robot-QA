#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Han"
__email__ = "liuhan132@foxmail.com"

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import time
import logging
from utils import sftp_get
from remote_service import MRCService, ASRService

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

QuestionAnswer = None
memory = None

logger = logging.getLogger(__name__)


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
            logger.info("Interrupted by user, shutting down")
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

        logger.info('Recording...')
        self.record.stopMicrophonesRecording()
        self.record.startMicrophonesRecording(self.tmp_audio_path, 'wav', self.rate, self.channels)
        time.sleep(6)
        self.record.stopMicrophonesRecording()
        logger.info('Record finished')

        logger.info('Downloading the audio from robot {}...'.format(self.ip))
        sftp_get(self.ip,
                 22,
                 NaoRobot.username,
                 NaoRobot.password,
                 self.tmp_audio_path,
                 self.tmp_audio_path)
        logger.info('Download finished')

        logger.info('Recognizing...')
        question = self.asr_service.recognize(self.tmp_audio_path, rate=self.rate)
        logger.info('Got the question: {}'.format(question))

        logger.info('Comprehending...')
        answer = MRCService.predict(self.context, question)
        logger.info('Got the answer: {}'.format(answer))

        if answer != '':
            self.asp.say(answer, self.configuration)
        else:
            self.asp.say('对不起，我不明白你在说什么。', self.configuration)

        # Subscribe again to the event
        memory.subscribeToEvent("SoundDetected",
                                "QuestionAnswer",
                                "onSoundDetected")


# ----------------------------------------------------------------------------------------------
# start running


import argparse
from utils import init_logging

context = '赵鹏（），中国足球运动员，司职后卫。赵鹏于1997年便加入河南建业青年队，2002年进入河南建业一线队。2011赛季结束后，' \
          '赵鹏和建业的合同完结，此后一直盛传他将加盟中超升班马广州富力。但最后在2012年1月12日，建业成功与赵鹏续约3年。2012赛季，' \
          '赵鹏未能帮助建业保级。其后在2013年1月1日，赵鹏连同其队友曾诚双双加盟广州恒大。 但球队中后卫位置的激烈竞争，再加上3月份他' \
          '在国家队比赛后的恢复训练受伤，直到5月10日，他才在广州恒大客场3比0击败上海申花的比赛下半场替补荣昊登场，首次为广州队在正式比' \
          '赛出场。2014年6月，赵鹏被租借到中超球队长春亚泰。 不过由于伤病困扰，他在2014下半赛季并没有得到出场机会。2016年3月，中乙球' \
          '队成都钱宝宣布赵鹏加盟。2009年赵鹏入选中国国家队，同年5月29日友谊赛对阵德国是他的第一场国际A级赛。'


def add_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description='NaoQi Robot with Question Answering\n'
                                                 'Contact: liuhan132@foxmail.com')
    parser.add_argument('-P', '--port', help='port', default=9559, required=False)
    parser.add_argument('-A', '--ip', help='ip', default='10.112.174.62', required=False)

    args = parser.parse_args()
    return args


def run():
    args = add_args()

    init_logging()
    nao = NaoRobot(args.ip, args.port)
    nao.connect()
    nao.run(context)


if __name__ == '__main__':
    run()