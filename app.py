import ipaddress
import os
import re
import logging
from datetime import timedelta, datetime

import boto3
import requests
from apscheduler.schedulers.blocking import BlockingScheduler

# 配置日志
logging.basicConfig(level=logging.INFO)

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
hosted_zone_id = os.getenv('HOST_ZONE_ID')
domain = os.getenv('DOMAIN')
old_ipv4 = None
old_ipv6 = None


def is_valid_ipv6(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        logging.error('不是正确的ipv6')
        return False


def get_local_ipv6():
    ip = None
    session = requests.Session()
    urls = [
        'https://speed.neu6.edu.cn/getIP.php',
        'https://v6.ident.me',
        'https://6.ipw.cn'
    ]
    for url in urls:
        try:
            response = session.get(url)
            response.raise_for_status()  # 将触发异常，如果状态不是200
            ip = response.text.strip()
            if ip and is_valid_ipv6(ip):
                break
        except requests.RequestException as e:
            logging.error(f"请求失败：{e}")
    return ip


def get_local_ipv4():
    ip = None
    session = requests.Session()
    urls = [
        'https://myip.ipip.net',
        'https://ddns.oray.com/checkip',
        'https://ip.3322.net',
        'https://4.ipw.cn'
    ]
    pattern = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')

    for url in urls:
        try:
            response = session.get(url)
            response.raise_for_status()  # 将触发异常，如果状态不是200
            ip = pattern.search(response.text)
            if ip:
                ip = ip.group()
                break
        except requests.RequestException as e:
            logging.error(f"请求失败：{e}")
    return ip


def change_ip(client, hz_id, new_ipv4, new_ipv6):
    change_ipv4 = {
        'Action': 'UPSERT',  # UPSERT表示如果记录存在则更新，不存在则创建
        'ResourceRecordSet': {
            'Name': domain,
            'Type': 'A',
            'TTL': 60,
            'ResourceRecords': [{'Value': new_ipv4}]
        }
    }
    change_ipv6 = {
        'Action': 'UPSERT',
        'ResourceRecordSet': {
            'Name': domain,
            'Type': 'AAAA',
            'TTL': 60,
            'ResourceRecords': [{'Value': new_ipv6}]
        }
    }
    # 发起更改请求
    response = client.change_resource_record_sets(
        HostedZoneId=hz_id,
        ChangeBatch={
            'Changes': [change_ipv4, change_ipv6]
        }
    )
    print(response['ChangeInfo']['Id'])


def job():
    global old_ipv4, old_ipv6
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    client = session.client('route53')
    local_ipv4 = get_local_ipv4()
    local_ipv6 = get_local_ipv6()
    logging.info(f'ipv4:{local_ipv4}')
    logging.info(f'ipv6:{local_ipv6}')
    if (local_ipv4 != old_ipv4) or (local_ipv6 != old_ipv6):
        logging.info("IP地址发生变化，正在更新DNS记录")
        old_ipv4 = local_ipv4
        old_ipv6 = local_ipv6
        change_ip(client, hosted_zone_id, local_ipv4, local_ipv6)
    else:
        logging.info("IP地址未发生变化")


def main():
    job_run_time = os.getenv('JOB_RUN_TIME')
    # 获取当前时间并减去1秒，以便立即执行
    first_run_time = datetime.now() - timedelta(seconds=1)
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'date', run_date=first_run_time, args=[], kwargs={}, misfire_grace_time=2)
    scheduler.add_job(job, 'interval', minutes=job_run_time, id='job_interval', misfire_grace_time=1)
    scheduler.start()


if __name__ == '__main__':
    main()
