# ledticker-pi
allows a raspberry pi to drive an LED display as an IOT divide in AWS.
The idea is to make a IOT thing that is basically just a slave to the messages
sent to a queue. This allows the device to be dumb and multiple suppliers to
be as sophisticated as needed.


## research and background
These are the guides that accelerated building this project extensively.

* Adafruit RGB Matrix Hat for RPI - https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi
* Controlling up to three chains of 64x64, 32x32, 16x32 or similar RGB LED displays using Raspberry Pi GPIO - https://github.com/hzeller/rpi-rgb-led-matrix
* Getting Started With RGB Matrix Panel - https://www.hackster.io/idreams/getting-started-with-rgb-matrix-panel-adaa49



## installing flashlex-pi-python

```
git clone https://github.com/claytantor/flashlex-pi-python.git
cd flashlex-pi-python
sudo python setup.py install
```

## install for python 3
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# running on cli
```
sudo /home/pi/projects/ledticker-pi/venv/bin/python -u /home/pi/projects/ledticker-pi/flashlex.py --led-no-hardware-pulse true -m adafruit-hat -r 32 --led-cols 32 --log DEBUG --config /home/pi/projects/ledticker-pi/config.yml 
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

# rotating logs
you will want to rotate logs so your disk doesnt fill up with logs. your conf file for logrotation looks like this in `/etc/logrotate.conf`:

```
/var/log/ledticker.log {
    daily
    missingok
    rotate 7
    maxage 7
    dateext
    dateyesterday
}
```

make a crontab that executes logrotate daily

```
/usr/sbin/logrotate /etc/logrotate.conf
```


