#!/bin/bash

PYTHON_PATH=$(which python3)
METRICS_PATH=$(pwd)

echo "Assuming DB entry already made"
echo "Crontab entries commented out"
sudo $PYTHON_PATH -m pip install schedule boto3 psutil mysql-connector-python ec2_metadata schedule
sed -i "s/<python>/$(echo $PYTHON_PATH)/g" metrics.service
sed -i "s/<metrics>/$(echo $METRICS_PATH)/g" metrics.service
sudo cp metrics.service /etc/systemd/system
echo "Placed service file, be sure to verify python location"
sudo systemctl daemon-reload
sudo systemctl enable metrics
sudo systemctl restart metrics
sudo systemctl status metrics
echo "Placing aliases"
echo "alias restartmetrics='sudo systemctl restart metrics'" >> $HOME/.bash_aliases
echo "alias stopmetrics='sudo systemctl stop metrics'" >> $HOME/.bash_aliases
echo "alias statusmetrics='sudo systemctl status metrics'" >> $HOME/.bash_aliases
echo "alias logmetrics='sudo journalctl -u metrics -f'" >> $HOME/.bash_aliases
source $HOME/.bash_aliases
echo "Done"
bash