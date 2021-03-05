#! /bin/bash

cp -r /home/pi/oc-rae/scripts/* /home/pi/environments/oc-rae/

cp /home/pi/oc-rae/config/collectData.service /etc/systemd/system
cp /home/pi/oc-rae/config/postData.service /etc/systemd/system
cp /home/pi/oc-rae/config/remoteSQL.service /etc/systemd/system
chown root:root /etc/systemd/system/collectData.service
chmod 644 /etc/systemd/system/collectData.service
chown root:root /etc/systemd/system/postData.service
chmod 644 /etc/systemd/system/postData.service
chown root:root /etc/systemd/system/remoteSQL.service
chmod 644 /etc/systemd/system/remoteSQL.service

systemctl daemon-reload

systemctl enable collectData.service
systemctl enable postData.service
systemctl enable remoteSQL.service

systemctl restart collectData.service
systemctl restart postData.service
systemctl restart remoteSQL.service

