import shutil
import psutil
from config import *
import datetime


def record_metrics():
    cpu_util = psutil.cpu_percent()
    mem_util = psutil.virtual_memory().percent
    mem_free = psutil.virtual_memory().available * 100 / psutil.virtual_memory().total

    # print(f"CPU utilization: {cpu_util}%")
    # print(f"RAM utilization: {mem_util}%")
    # print(f"Free memory: {mem_free}%")
    metrics = {
        "cpu_util": cpu_util,
        "mem_util": mem_util,
        "mem_free": mem_free
    }

    for drive in DISK_DRIVES:
        total, used, free = shutil.disk_usage(drive)
        util = (used / total) * 100
        # print("Total: %d GiB" % (total // (2 ** 30)))
        # print("Used: %d GiB" % (used // (2 ** 30)))
        # print("Free: %d GiB" % (free // (2 ** 30)))
        # print(f"{drive} utilization: {util}%")
        metrics[f"disk_util_{drive}"] = util

    persist_metrics(metrics)


def persist_metrics(metrics):
    try:
        # print(metrics)
        now = datetime.datetime.now()
        metric_keys = metrics.keys()
        for metric in metric_keys:
            # print(f"{metric} - {metrics[metric]}")
            sql = f"INSERT INTO graphing_data.server_metrics(hostname, timestamp, metric, value) " \
                  f"VALUES('{HOSTNAME}', '{now}', '{metric}', '{metrics[metric]}')"
            # print(sql)
            cursor.execute(sql)
        db.commit()

        print(f"Inserted into DB: {metrics}")
    except Exception as e:
        print(e)


record_metrics()
