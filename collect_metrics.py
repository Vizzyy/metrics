import json
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
import boto3

metrics = {}
db = None
cursor = None
args = None
sqs = boto3.client('sqs')


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


def record_directory_size():
    import os  # limit this import to those that have this enabled
    global metrics
    for directory in DIRECTORIES:
        try:
            usage = os.popen(f'du -sm {directory} | cut -f1')  # return megabytes
            metrics[f"dir_size_{directory}"] = int(usage.read())
        except Exception as e:
            print(f"Could not size for {directory} due to: {e}")


def record_psu_stats():
    import os
    global metrics
    try:
        usage = os.popen(f'sudo /usr/sbin/pwrstat -status').read()
        print(usage)

        bits = usage.split('\n')

        stats_map = {}

        for line in bits[7:]:
            if '..' not in line:
                continue
            else:
                key, value = line.strip().split('. ')
                key = key.replace('.', '')
                if key == 'Test Result':
                    test_result = value.split()
                    stats_map['Test Result'] = test_result[0]
                    stats_map['Test Result Datetime'] = f'{test_result[2]} {test_result[3]}'
                else:
                    stats_map[key] = value.split(' ')[0]

        print(stats_map)

        for metric in stats_map.keys():
            metrics[f'psu_{metric}'] = stats_map[metric]

    except Exception as e:
        print(f"{type(e).__name__} - {e}")


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


def record_cert_expiry():
    import os
    for host in cert_expiry_hosts:
        try:
            usage = os.popen(f'echo "Q" | openssl s_client -showcerts -servername {host} -connect {host}:443 | openssl x509 -noout -dates')
            response = usage.read().strip().split("notAfter=")[-1]
            datetime_object = datetime.datetime.strptime(response, '%b %d %H:%M:%S %Y %Z')
            date_today = datetime.datetime.now()
            days_until_expiration = (datetime_object - date_today).days
            metrics[f"cert_{host}"] = days_until_expiration
        except Exception as e:
            print(f"Could not check cert on {host} due to: {e}")
            continue

        # print(f"Host {host} cert expires: {datetime_object}, in {days_until_expiration} days.")


def record_soil_moisture():
    try:
        import board
        import busio
        import adafruit_ads1x15.ads1115 as ADS
        from adafruit_ads1x15.analog_in import AnalogIn

        max_value = moisture_calibration_max
        min_value = moisture_calibration_min
        diff_value = max_value - min_value

        # Create the I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)

        # Create the ADC object using the I2C bus
        ads = ADS.ADS1115(i2c)

        # Create single-ended input on channel 0
        chan = AnalogIn(ads, ADS.P0)

        curr_value = chan.value

        moisture_level = 100 - (((curr_value - min_value) / diff_value) * 100)

        if moisture_level > 100:
            moisture_level = 100
        if moisture_level < 0:
            moisture_level = 0

        metrics[f"soil_mositure"] = moisture_level

        # print(f"Current: {curr_value} - Moisture Level: {moisture_level}%")

    except Exception as e:
        print(f"ERROR: {type(e).__name__} while recording soil moisture - {e.args}")
        pass


def record_internet_metrics():
    from subprocess import STDOUT, check_output

    try:
        usage = check_output('speedtest -f json'.split(' '), stderr=STDOUT, timeout=180).decode("utf-8")
        api_result = None
        for block in usage.splitlines():
            try:
                block_obj = json.loads(block)
                if block_obj["type"] == "result":
                    api_result = block_obj
            except Exception as e:
                print(f"Parsing speedtest cli blocks: {type(e).__name__} - {e}")

        if not api_result:
            print(usage)
            raise Exception("No viable api result!")

        metrics[f"internet_jitter"] = float(api_result["ping"]["jitter"])  # milliseconds
        metrics[f"internet_latency"] = float(api_result["ping"]["latency"])  # milliseconds
        metrics[f"internet_download"] = (int(api_result["download"]["bandwidth"]) * 8) / 1000 / 1000  # Mbps
        metrics[f"internet_upload"] = (int(api_result["upload"]["bandwidth"]) * 8) / 1000 / 1000  # Mbps
    except Exception as e:
        print(f"[{type(e).__name__}] Could not gather internet metrics due to: {e}")


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


def sqs_send():
    global args, metrics

    queue_url = args.queue
    now = datetime.datetime.now()

    message = {
        "action": "insert",
        "table": "server_metrics",
        "values": {
            "hostname": HOSTNAME,
            "timestamp": now.__str__(),
            "metrics": metrics
        }
    }

    # Send message to SQS queue
    print(f"Pushing message to queue: {metrics}")
    response = sqs.send_message(QueueUrl=queue_url, MessageBody=(json.dumps(message)))
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise RuntimeError("Could not enqueue message!")


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def every_minute_job():
    global args, metrics

    if args.cpu_util: record_cpu_util(args.ec2)
    if args.cpu_load: record_avg_cpu_load()
    if args.mem_util: record_mem_util(args.ec2)
    if args.cpu_temp: record_cpu_temp(args.osx)
    if args.network_sent: record_network_sent(args.exclude_lo)
    if args.network_recv: record_network_recv(args.exclude_lo)
    if args.network_sent_avg: record_network_sent_avg()
    if args.network_recv_avg: record_network_recv_avg()
    if args.queue_depth: record_queue_depth()
    if args.climate: record_climate()
    if args.dir_size: record_directory_size()
    if args.soil_moisture: record_soil_moisture()
    if args.psu_stats: record_psu_stats()
    if args.persist:
        sqs_send()
    else:
        print(f"Minute Metrics: {metrics}")

    metrics = {}  # reset metrics object


def record_internet_metrics_job():
    global args, metrics

    if args.internet: record_internet_metrics()
    if args.persist and len(metrics.keys()) > 0:
        sqs_send()
    else:
        print(f"record_internet_metrics_job Metrics: {metrics}")

    metrics = {}  # reset metrics object


def every_hour_job():
    global args, metrics

    if args.uptime: record_uptime()
    if args.aws_cost: record_aws_cost()
    if args.disk_util: record_disk_util()
    if args.cert_expiry: record_cert_expiry()
    if args.persist:
        sqs_send()
    else:
        print(f"Hour Metrics: {metrics}")

    metrics = {}  # reset metrics object


if __name__ == "__main__":

    if not db:
        initialize_db_conn()

    args = Struct(**pull_host_args())

    schedule.every().minute.do(every_minute_job)
    schedule.every(10).minutes.do(record_internet_metrics_job)
    schedule.every().hour.do(every_hour_job)

    every_minute_job()  # run all metrics once immediately
    every_hour_job()
    record_internet_metrics_job()

    while args.daemon:
        schedule.run_pending()
        time.sleep(1)
