import datetime
from config import *


def get_network_avg(metric):
    result = 0
    results = 0.0
    now = datetime.datetime.now()
    five_minutes = datetime.timedelta(minutes=5)
    five_minutes_ago = now - five_minutes
    # print(now)
    try:
        cursor = db.cursor(dictionary=True)
        sql = f"select * from graphing_data.server_metrics " \
              f"where hostname = '{HOSTNAME}' " \
              f"and metric = '{metric}' " \
              f"and timestamp >= '{five_minutes_ago}' " \
              f"ORDER BY timestamp DESC"
        cursor.execute(sql)
        query_results = cursor.fetchall()
        print(f"Found {len(query_results)} entries")
        for i in range(0, len(query_results)):
            try:
                temp = float(query_results[i]['value'] - query_results[i+1]['value'])
                print(f"temp: {temp}")
                results += temp
            except IndexError:
                print("IndexError")
                break

        avg = results / float(len(query_results))
        print(f"{metric} avg: {avg}")

        if avg < 0:
            avg = 0

        result = avg
    except ZeroDivisionError:
        print("ZeroDivisionError")
        pass
    except Exception as e:
        print(f"Network Avg error: {e}")
    return result
