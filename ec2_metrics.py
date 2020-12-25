import boto3
from datetime import datetime, timedelta, date

from ec2_metadata import ec2_metadata


def get_ec2_metric(namespace, metric_name, custom_dimensions=None, period=300, statistic='Average', unit='Percent',
                   start_time_seconds=300):
    client = boto3.client('cloudwatch')

    if custom_dimensions is not None:
        dimensions = custom_dimensions
    else:
        dimensions = [
            {
                'Name': 'InstanceId',
                'Value': ec2_metadata.instance_id
            },
        ]

    response = client.get_metric_statistics(
        Namespace=namespace,
        MetricName=metric_name,
        Dimensions=dimensions,
        StartTime=datetime.utcnow() - timedelta(seconds=start_time_seconds),
        EndTime=datetime.utcnow(),
        Period=period,
        Statistics=[
            statistic,
        ],
        Unit=unit
    )
    try:
        result = response["Datapoints"][0][statistic]
    except Exception as e:
        print(e)
        result = 0
        print(response)
    return result


def get_aws_cost():
    return get_ec2_metric('AWS/Billing', 'EstimatedCharges', [{'Name': 'Currency', 'Value': 'USD'}], 60, 'Maximum',
                          'None', 30000)


def get_ec2_cpu():
    return get_ec2_metric('AWS/EC2', 'CPUUtilization')


def get_ec2_mem():
    return get_ec2_metric('CWAgent', 'mem_used_percent')


def get_ec2_network_in():
    return get_ec2_metric('AWS/EC2', 'NetworkIn')


def get_ec2_network_out():
    return get_ec2_metric('AWS/EC2', 'NetworkOut')
