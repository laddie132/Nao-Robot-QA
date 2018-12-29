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

context = '于乐（），中国足球运动员，司职前锋。于乐出身于北京国安，在2006年以2万元转会到河南建业。2007年赛季，河南建业对阵大连实德，' \
          '于乐下半场打进制胜一球，帮助球队获得队史首场中超胜利而一战成名。不过随后由于上阵机会不多成为球队的边缘球员。2010年河南建业' \
          '要在中超和亚冠双线作战，在伤兵满营的情况下于乐才获得出场机会，当年4月13日进行的亚足联冠军联赛客场对阵新加坡武装部队的比赛中，' \
          '于乐为河南建业一度扳平比分，收获个人首个亚冠进球，可惜球队最终以1-2失利。该赛季，于乐在中超出场15次打进3球。2011年于乐在中超' \
          '联赛只出场7次，其中首发1次，全部出场时间加起来只有184分钟。2012年2月，于乐以自由转会方式加盟深圳红钻与球队签约3年，合同到期后' \
          '深圳红钻有续约1年的优先权。由于遭遇伤病影响，未有过多发挥。2013年，于乐摆脱伤病困扰恢复状态，成为深圳队锋线上颇具冲击力的福将，' \
          '赛季中期状态火爆屡屡打入关键入球。'


def add_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description='NaoQi Robot with Question Answering\n'
                                                 'Contact: liuhan132@foxmail.com')
    parser.add_argument('-P', '--port', help='port', default=9559, required=False)
    parser.add_argument('-A', '--ip', help='ip', default='10.112.156.141', required=False)

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
