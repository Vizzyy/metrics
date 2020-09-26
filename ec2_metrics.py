import boto3
from datetime import datetime, timedelta

from ec2_metadata import ec2_metadata


def get_ec2_metric(namespace, metricname):
    client = boto3.client('cloudwatch')
    response = client.get_metric_statistics(
        Namespace=namespace,
        MetricName=metricname,
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': ec2_metadata.instance_id
            },
        ],
        StartTime=datetime.today() - timedelta(seconds=300),
        EndTime=datetime.today(),
        Period=300,
        Statistics=[
            'Average',
        ],
        Unit='Percent'
    )
    result = response["Datapoints"][0]["Average"]
    # print(result)
    return result


def get_ec2_cpu():
    return get_ec2_metric('AWS/EC2', 'CPUUtilization')


def get_ec2_mem():
    return get_ec2_metric('System/Linux', 'MemoryUtilization')

