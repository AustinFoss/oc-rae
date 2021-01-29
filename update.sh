#!/bin/bash

systemctl stop collectData.service

git pull

sudo -u pi psql << EOF
DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS data_collection;
EOF

# Copy Python scripts to the virtual environment
cp -r /home/pi/oc-rae/scripts/* /home/pi/environments/oc-rae/
# Copy PostgreSQL configuration files to enable remote access
cp /home/pi/oc-rae/config/postgresql.conf /etc/postgresql/11/main/
cp /home/pi/oc-rae/config/pg_hba.conf /etc/postgresql/11/main/
# Copy config file to enable the Raspberry Pi Camera
cp /home/pi/oc-rae/config/config.txt /boot/
# Copy samba config file
cp /home/pi/oc-rae/config/smb.conf /etc/samba/smb.conf
chown root:root /etc/samba/smb.conf

# Ensure all directories created belong to the user 'pi'
chown -R pi:pi /home/pi
chmod -R 777 /home/pi/oc-rae

# Install all required python packages in the virtual environment
source /home/pi/environments/oc-rae/bin/activate
pip install -r /home/pi/environments/oc-rae/requirements.txt
deactivate

# Enable the Python script(s) as services the start on reboot and restart after failures
cp /home/pi/oc-rae/config/collectData.service /etc/systemd/system
cp /home/pi/oc-rae/config/postData.service /etc/systemd/system
chown root:root /etc/systemd/system/collectData.service
chmod 644 /etc/systemd/system/collectData.service
chown root:root /etc/systemd/system/postData.service
chmod 644 /etc/systemd/system/postData.service
systemctl daemon-reload
systemctl enable collectData.service
systemctl enable postData.service

reboot
