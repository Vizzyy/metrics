#!/bin/bash

echo "Assuming DB entry already made"
echo "Crontab entries commented out"
git fetch --all
git stash
git checkout daemon
pip3 install schedule
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