ZJU jwb to iCalendar
====================

将浙江大学教务网课程导出为 iCalendar 文件（可用于 iCal、Google Calendar 等）。

## 使用方法

### 在线使用

感谢 @starrify 将项目 port 到 OpenShift 上。

* http://zjujwbtools-starrify.rhcloud.com/ （被墙，请自行翻越）
* http://zjujwbtools.starrybo.at/ （CNAME 到如上地址，没有被墙）

你也可以自行部署到 OpenShift，详情：https://github.com/xhacker/zju-jwb-to-icalendar/pull/3 。

### 命令行使用

```bash
./grabber.py username password [output_file]
```

## 欢迎 Pull Request

由于每个学期需要更新数据，且教务网有可能发生变化，故长期欢迎各类 pull request。

## 已知问题

无法处理因为节假日产生的调课。

另外，脚本可能有纰漏，由于使用本脚本造成的上课迟到、挂科，作者概不负责。

## 授权许可
MIT
