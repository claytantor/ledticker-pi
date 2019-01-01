# ledticker-pi
allows a raspberry pi to drve an LED display as an IOT devide in AWS.

## research and background

* Adafruit RGB Matrix Hat for RPI - https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi
* Controlling up to three chains of 64x64, 32x32, 16x32 or similar RGB LED displays using Raspberry Pi GPIO - https://github.com/hzeller/rpi-rgb-led-matrix
* Getting Started With RGB Matrix Panel - https://www.hackster.io/idreams/getting-started-with-rgb-matrix-panel-adaa49


## install for python 2.7
```
virtualenv venv
curl https://bootstrap.pypa.io/get-pip.py | python
pip install --upgrade pip
pip install -r requirements.txt
```

## updating your rasperry pi
```
sudo apt-get update
sudo apt-get -y install python-dev python3-rpi.gpio
sudo apt-get -y install i2c-tools
sudo apt-get y install python-smbus

virtualenv --system-site-packages venv
pip install -r requirements.txt
pip install --no-cache-dir PyYAML
```

## creating the systemd service
Instructions for setting up your service can be found at https://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd/

```
sudo cp ledticker.service /lib/systemd/system/ledticker.service
sudo chmod 644 /lib/systemd/system/ledticker.service
sudo systemctl daemon-reload
sudo systemctl enable ledticker.service
```

## add logging to syslog

Then, assuming your distribution is using rsyslog to manage syslogs, create a file in /etc/rsyslog.d/<new_file>.conf with the following content:

if $programname == '<your program identifier>' then /path/to/log/file.log
& stop
restart rsyslog (sudo systemctl restart rsyslog) and enjoy! Your program stdout/stderr will still be available through journalctl (sudo journalctl -u <your program identifier>) but they will also be available in your file of choice. 

```
sudo cp ledticker.conf /etc/rsyslog.d/ledticker.conf 
sudo systemctl daemon-reload
sudo systemctl restart ledticker.service
sudo systemctl restart rsyslog
```

## check the status of the service
```
sudo systemctl status ledticker.service
```


