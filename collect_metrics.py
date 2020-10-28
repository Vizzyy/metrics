import argparse
import math
import shutil
import psutil
from config import *
import datetime
import time
from ec2_metrics import get_ec2_cpu, get_ec2_mem
from network_metrics import get_network_avg


metrics = {}


def arguments():
    parser = argparse.ArgumentParser(description='A script that records server metrics.')
    parser.add_argument('--cpu_util', help='Record CPU Utilization.', action='store_true')
    parser.add_argument('--cpu_load', help='Record CPU load average.', action='store_true')
    parser.add_argument('--network_sent', help='Record network bytes sent.', action='store_true')
    parser.add_argument('--network_recv', help='Record network bytes received.', action='store_true')
    parser.add_argument('--network_sent_avg', help='Record 5 min avg of bytes sent.', action='store_true')
    parser.add_argument('--network_recv_avg', help='Record 5 min avg of bytes received.', action='store_true')
    parser.add_argument('--mem_util', help='Record Memory Utilization.', action='store_true')
    parser.add_argument('--disk_util', help='Record Disk Utilization.', action='store_true')
    parser.add_argument('--cpu_temp', help='Record CPU temperature.', action='store_true')
    parser.add_argument('--uptime', help='Record server uptime.', action='store_true')
    parser.add_argument('--persist', help='Persists metrics into DB.', action='store_true')
    parser.add_argument('--ec2', help='Use Boto3 for more accurate metrics.', action='store_true')
    parser.add_argument('--all', help='Gather all metrics. (Does not include EC2 flag)', action='store_true')
    return parser.parse_args()


def record_cpu_util(ec2):
    global metrics
    if ec2:
        cpu_util = get_ec2_cpu()
    else:
        cpu_util = psutil.cpu_percent()
    metrics["cpu_util"] = cpu_util


def record_avg_cpu_load():
    # Returns tuple of processes in the system run queue averaged over the last 1, 5, and 15 minutes
    # We select the avg of last minute (pos. 0)
    cpu_load = psutil.getloadavg()[0]
    metrics["cpu_load"] = cpu_load


def record_network_sent():
    metrics["network_sent"] = psutil.net_io_counters().bytes_sent


def record_network_sent_avg():
    five_min_avg = get_network_avg("network_sent")
    metrics["network_sent_avg"] = five_min_avg


def record_network_recv():
    metrics["network_recv"] = psutil.net_io_counters().bytes_recv


def record_network_recv_avg():
    five_min_avg = get_network_avg("network_recv")
    metrics["network_recv_avg"] = five_min_avg


def record_mem_util(ec2):
    global metrics
    if ec2:
        mem_util = get_ec2_mem()
    else:
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
    if args.cpu_util or args.all:
        record_cpu_util(args.ec2)
    if args.cpu_load or args.all:
        record_avg_cpu_load()
    if args.mem_util or args.all:
        record_mem_util(args.ec2)
    if args.disk_util or args.all:
        record_disk_util()
    if args.cpu_temp or args.all:
        record_cpu_temp()
    if args.uptime or args.all:
        record_uptime()
    if args.network_sent or args.all:
        record_network_sent()
    if args.network_recv or args.all:
        record_network_recv()
    if args.network_sent_avg or args.all:
        record_network_sent_avg()
    if args.network_recv_avg or args.all:
        record_network_recv_avg()
    if args.persist or args.all:
        persist_metrics()
    else:
        print(f"Metrics: {metrics}")

