import math
import shutil
import psutil
from config import *
import datetime
import time
from ec2_metrics import get_ec2_cpu, get_ec2_mem, get_aws_cost, get_queue_depth
from climate import get_climate_measurements
import mysql.connector
import schedule

metrics = {}
db = None
cursor = None
args = None


def record_cpu_util(ec2):
    global metrics
    if ec2:
        cpu_util = get_ec2_cpu()
    else:
        cpu_util = psutil.cpu_percent()
    metrics["cpu_util"] = cpu_util


def record_avg_cpu_load():
    global metrics
    # Returns tuple of processes in the system run queue averaged over the last 1, 5, and 15 minutes
    # We select the avg of last minute (pos. 0)
    cpu_load = psutil.getloadavg()[0]
    num_physical_cores = psutil.cpu_count(logical=False)
    if num_physical_cores > 1:
        metrics["cpu_load_multi_core"] = cpu_load
    else:
        metrics["cpu_load_single_core"] = cpu_load
    metrics["cpu_load"] = cpu_load


def record_network_sent(exclude_lo):
    global metrics
    if exclude_lo:
        net_io = psutil.net_io_counters(pernic=True)
        total_bytes = 0
        for interface in net_io.keys():
            if "lo" not in interface:
                total_bytes += net_io[interface].bytes_sent
        metrics["network_sent"] = total_bytes / 1024 / 1024
    else:
        metrics["network_sent"] = psutil.net_io_counters().bytes_sent / 1024 / 1024


def record_network_sent_avg():
    global metrics
    five_min_avg = get_network_avg("network_sent")
    metrics["network_sent_avg"] = five_min_avg


def record_network_recv(exclude_lo):
    global metrics
    if exclude_lo:
        net_io = psutil.net_io_counters(pernic=True)
        total_bytes = 0
        for interface in net_io.keys():
            if "lo" not in interface:
                total_bytes += net_io[interface].bytes_recv
        metrics["network_recv"] = total_bytes / 1024 / 1024
    else:
        metrics["network_recv"] = psutil.net_io_counters().bytes_recv / 1024 / 1024


def record_network_recv_avg():
    global metrics
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


def record_cpu_temp(osx):
    global metrics
    try:
        if not osx:
            # Should work on any non-Mac linux box
            cpu_temp = psutil.sensors_temperatures()[list(psutil.sensors_temperatures())[0]][0][1]
            metrics["cpu_temp"] = cpu_temp
        else:
            import os
            stream = os.popen('/usr/local/bin/osx-cpu-temp')
            cpu_temp = stream.read().split(" ")[0]
            metrics["cpu_temp"] = cpu_temp

    except Exception as e:
        print(e)


def record_uptime():
    global metrics
    seconds_uptime = time.time() - psutil.boot_time()
    days_uptime = math.floor(seconds_uptime / (3600 * 24))
    metrics["uptime"] = days_uptime


def record_climate():
    global metrics
    climate_readings = get_climate_measurements()
    metrics["climate_humid"] = climate_readings[0]
    metrics["climate_temp_c"] = climate_readings[1]
    fahrenheit = (climate_readings[1] * 9 / 5) + 32
    metrics["climate_temp_f"] = fahrenheit


def record_aws_cost():
    global metrics
    metrics["aws_cost"] = get_aws_cost()


def record_queue_depth():
    global metrics
    metrics["queue_depth"] = get_queue_depth(queue_name)


def initialize_db_conn():
    global db, cursor
    try:
        db = mysql.connector.connect(**SSL_CONFIG)
        print("Connected to DB!")
        return True
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return False


def get_network_avg(metric):
    result = 0
    results = 0.0
    now = datetime.datetime.now()
    five_minutes = datetime.timedelta(minutes=5)
    five_minutes_ago = now - five_minutes
    try:
        db.ping(True)
        cursor = db.cursor(dictionary=True)
        sql = f"select * from graphing_data.server_metrics " \
              f"where hostname = %s " \
              f"and metric = %s " \
              f"and timestamp >= %s " \
              f"ORDER BY timestamp DESC"
        cursor.execute(sql, (HOSTNAME, metric, five_minutes_ago))
        query_results = cursor.fetchall()
        cursor.close()
        for i in range(0, len(query_results)):
            try:
                temp = float(query_results[i]['value'] - query_results[i+1]['value'])
                results += temp
            except IndexError:
                break

        avg = results / float(len(query_results))

        if avg < 0:
            avg = 0

        result = avg
    except ZeroDivisionError:
        pass
    except Exception as e:
        print(f"Network Avg error: {e}")
    return result


def persist_metrics():
    global db, cursor, metrics
    try:
        db.ping(True)
        now = datetime.datetime.now()
        metric_keys = metrics.keys()
        cursor = db.cursor()
        for metric in metric_keys:
            params = (HOSTNAME, now, metric, metrics[metric])
            sql = f"INSERT INTO graphing_data.server_metrics(hostname, timestamp, metric, value) " \
                  f"VALUES(%s, %s, %s, %s)"
            cursor.execute(sql, params)
        db.commit()
        cursor.close()
        print(f"Inserted into DB: {metrics}")
        metrics = {}
    except Exception as e:
        print(f"Error Persisting Metrics: {e}")


def pull_host_args():
    global db, cursor
    remote_args = None

    try:
        db.ping(True)
        cursor = db.cursor(dictionary=True)
        sql = "select * from graphing_data.metric_host_args where host = %s"
        cursor.execute(sql, (HOSTNAME,))
        remote_args = cursor.fetchall()[0]
        cursor.close()
        print(f"Pulled host args: {remote_args}")
    except Exception as e:
        print(f"Error pulling host args: {e}")

    return remote_args


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def every_minute_job():
    global args

    if args.cpu_util: record_cpu_util(args.ec2)
    if args.cpu_load: record_avg_cpu_load()
    if args.mem_util: record_mem_util(args.ec2)
    if args.disk_util: record_disk_util()
    if args.cpu_temp: record_cpu_temp(args.osx)
    if args.network_sent: record_network_sent(args.exclude_lo)
    if args.network_recv: record_network_recv(args.exclude_lo)
    if args.network_sent_avg: record_network_sent_avg()
    if args.network_recv_avg: record_network_recv_avg()
    if args.queue_depth: record_queue_depth()
    if args.climate: record_climate()
    if args.persist:
        persist_metrics()
    else:
        print(f"Metrics: {metrics}")


def every_hour_job():
    global args

    if args.uptime: record_uptime()
    if args.aws_cost: record_aws_cost()
    if args.persist:
        persist_metrics()
    else:
        print(f"Metrics: {metrics}")


if __name__ == "__main__":

    if not db:
        initialize_db_conn()

    args = Struct(**pull_host_args())

    schedule.every().minute.do(every_minute_job)
    schedule.every().hour.do(every_hour_job)

    while True:

        if not args.daemon:
            every_minute_job()
            every_hour_job()
            break
        else:
            schedule.run_pending()
            time.sleep(1)
