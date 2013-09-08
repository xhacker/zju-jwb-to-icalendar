ZJU jwb to iCalendar
====================

将浙江大学教务网课程导出为 iCalendar 文件（可用于 iCal、Google Calendar 等）。

## 使用方法

0. 安装 pip
1. `sudo pip install -r requirements.txt`
2. `python grabber.py`
3. 验证码会保存到 `captcha.gif`
4. 输入学号、密码、验证码
5. 文件会导出到 `dump.ics` 和 `dump.yaml`

## 欢迎 Pull Request

由于每个学期需要更新数据，且教务网有可能发生变化，故长期欢迎各类 pull request。

## 已知问题

无法处理因为节假日产生的调课。

另外，脚本可能有纰漏，由于使用本脚本造成的上课迟到、挂科，作者概不负责。
