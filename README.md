# Nao-Robot-MRC

本项目基于研究生智能机器人实验课程和机器阅读理解任务，实现了一个问答机器人。

## Machine Reading Comprehension
使用改进的Match-LSTM模型，也称作GM-Reader模型。

## Requirements
- python2.7
- requests
- aip
- paramiko
- yaml

## Help

```bash
usage: run_robot.py [-h] [-P PORT] [-A IP]

NaoQi Robot with Question Answering
Contact: liuhan132@foxmail.com

optional arguments:
  -h, --help            show this help message and exit
  -P PORT, --port PORT  port
  -A IP, --ip IP        ip

```

## Reference
- https://github.com/laddie132/Match-LSTM
- https://github.com/laddie132/Match-LSTM-CMRC