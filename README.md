# Ddns-py
自动获得你的公网 IPv4 或 IPv6 地址，并解析到AWS R53服务。
可以用于家庭网络的ddns，也可以用于ec2，可以帮助ec2节约弹性IP的费用。

## 运行命令
docker run -d --name ddns-py --restart=always --net=host -e AWS_ACCESS_KEY_ID='' -e AWS_SECRET_ACCESS_KEY='' -e HOST_ZONE_ID='' -e DOMAIN='' -e JOB_RUN_TIME='3' jeessy/ddns-go

## 环境变量说明
| 变量名                   | 说明                             |
|-----------------------|--------------------------------|
| AWS_ACCESS_KEY_ID     | IAM账号的ACCESS_KEY               |
| AWS_SECRET_ACCESS_KEY | IAM账号的SECRET_ACCESS_KEY        |
| HOST_ZONE_ID          | 托管区域ID                         |
| DOMAIN                | 要解析的域名（域名要到根例如：www.baidu.com.） |
| JOB_RUN_TIME          | 脚本执行的时间间隔（我自己设置的是3分钟，看个人需要。）   |
* **以上环境变量必填。**

## DockerHub地址
> https://hub.docker.com/r/tengsihai/ddns-py/tags