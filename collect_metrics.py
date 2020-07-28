import argparse
import math
import shutil
import psutil
from config import *
import datetime
import time


metrics = {}


def arguments():
    parser = argparse.ArgumentParser(description='A script that records server metrics.')
    parser.add_argument('--cpu_util', help='Record CPU Utilization.', action='store_true')
    parser.add_argument('--mem_util', help='Record Memory Utilization.', action='store_true')
    parser.add_argument('--disk_util', help='Record Disk Utilization.', action='store_true')
    parser.add_argument('--cpu_temp', help='Record CPU temperature.', action='store_true')
    parser.add_argument('--uptime', help='Record server uptime.', action='store_true')
    parser.add_argument('--persist', help='Persists metrics into DB.', action='store_true')
    return parser.parse_args()


def record_cpu_util():
    global metrics
    cpu_util = psutil.cpu_percent()
    metrics["cpu_util"] = cpu_util


def record_mem_util():
    global metrics
    mem_util = psutil.virtual_memory().percent
    metrics["mem_util"] = mem_util


def record_disk_util():
    global metrics
    for drive in DISK_DRIVES:
        total, used, free = shutil.disk_usage(drive)
        util = (used / total) * 100
        metrics[f"disk_util_{drive}"] = util


def record_cpu_temp():
    global metrics
    try:
        # Should work on any non-Mac linux box
        cpu_temp = psutil.sensors_temperatures()[list(psutil.sensors_temperatures())[0]][0][1]
        metrics["cpu_temp"] = cpu_temp
    except Exception as e:
        print(e)


def record_uptime():
    global metrics
    seconds_uptime = time.time() - psutil.boot_time()
    days_uptime = math.floor(seconds_uptime / (3600*24))
    metrics["uptime"] = days_uptime


def persist_metrics():
    global metrics
    try:
        now = datetime.datetime.now()
        metric_keys = metrics.keys()
        for metric in metric_keys:
            sql = f"INSERT INTO graphing_data.server_metrics(hostname, timestamp, metric, value) " \
                  f"VALUES('{HOSTNAME}', '{now}', '{metric}', '{metrics[metric]}')"
            cursor.execute(sql)
        db.commit()
        print(f"Inserted into DB: {metrics}")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    args = arguments()
    if args.cpu_util:
        record_cpu_util()
    if args.mem_util:
        record_mem_util()
    if args.disk_util:
        record_disk_util()
    if args.cpu_temp:
        record_cpu_temp()
    if args.uptime:
        record_uptime()
    if args.persist:
        persist_metrics()
    else:
        print(f"Metrics: {metrics}")

