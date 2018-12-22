#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'han'

import sys
import yaml
import paramiko
import logging.config


def init_logging(config_path='config/logging_config.yaml'):
    """
    initial logging module with config
    :param config_path:
    :return:
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    except IOError:
        sys.stderr.write('logging config file "%s" not found' % config_path)
        logging.basicConfig(level=logging.DEBUG)


def sftp_get(ip, port, username, password, remote_file, local_file):
    try:
        t = paramiko.Transport(sock=(ip, port))
        t.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.get(remote_file, local_file)
        t.close()
    except Exception as e:
        logging.error(e)
