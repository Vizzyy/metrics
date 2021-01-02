#!/bin/bash

PYTHON_PATH=$1
METRICS_PATH=$2

echo "Assuming DB entry already made"
echo "Crontab entries commented out"
pip3 install schedule
echo 'sed -i "s/<python>/$PYTHON_PATH/g" metrics.service'
echo 'sed -i "s/<metrics>/$METRICS_PATH/g" metrics.service'
sudo cp metrics.service /etc/systemd/system
echo "Placed service file, be sure to verify python location"
sudo systemctl daemon-reload
sudo systemctl enable metrics
sudo systemctl restart metrics
sudo systemctl status metrics
echo "Placing aliases"
echo "alias restartmetrics='sudo systemctl restart metrics'" >> /home/pi/.bash_aliases
echo "alias stopmetrics='sudo systemctl stop metrics'" >> /home/pi/.bash_aliases
echo "alias statusmetrics='sudo systemctl status metrics'" >> /home/pi/.bash_aliases
echo "alias logmetrics='sudo journalctl -u metrics -f'" >> /home/pi/.bash_aliases
source /home/pi/.bash_aliases
echo "Done"
bash