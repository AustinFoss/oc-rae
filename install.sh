#!/bin/bash

# Make the folder where all pictures from the Raspberry Pi  Camera will be stored
mkdir /home/pi/oc-rae/Pictures
# Initialize the working Python virtual environment
python3 -m venv /home/pi/environments/oc-rae

# Configure the PostgreSQL user
sudo -u postgres createuser -s pi
sudo -u postgres createdb pi
sudo -u pi psql << EOF
ALTER ROLE pi WITH PASSWORD 'oldsCollege';
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
chown root:root /etc/systemd/system/collectData.service
chmod 644 /etc/systemd/system/collectData.service
systemctl daemon-reload
systemctl enable collectData.service

#Set Samba user password
smbpasswd -a pi

# Finish installation and reboot
reboot