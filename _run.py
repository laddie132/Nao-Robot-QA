#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Han"
__email__ = "liuhan132@foxmail.com"

"""Not used beacuse of the global variable issue"""

import argparse
from utils import init_logging
from run_robot import NaoRobot


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