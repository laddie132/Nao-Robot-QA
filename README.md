# Nao-Robot-MRC

本项目基于Nao机器人和机器阅读理解任务，实现了一个问答机器人程序。

## Machine Reading Comprehension
使用改进的[Match-LSTM](https://github.com/laddie132/Match-LSTM)模型，中文项目为[Match-LSTM-CMRC](https://github.com/laddie132/Match-LSTM-CMRC/tree/nao-robot)。

## Requirements
- python2.7
- requests
- aip
- paramiko
- yaml

## Help
首先配置服务端，具体可参考[Match-LSTM-CMRC](https://github.com/laddie132/Match-LSTM-CMRC/tree/nao-robot)项目，示例代码如下：
```bash
git clone https://github.com/laddie132/Match-LSTM-CMRC
cd Match-LSTM-CMRC
git checkout nao-robot
python run_service.py
```

成功启动服务端后，运行如下程序启动客户端程序：
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
- https://github.com/laddie132/Match-LSTM-CMRC/tree/nao-robot
