# doorman
allows a raspberry pi to open a door with a key code in the cloud.


sudo apt-get update
sudo apt-get -y install python-dev python3-rpi.gpio
sudo apt-get -y install i2c-tools
sudo apt-get y install python-smbus

virtualenv --system-site-packages venv
pip install -r requirements.txt
pip install --no-cache-dir PyYAML


#led matrix

https://github.com/hzeller/rpi-rgb-led-matrix 

https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi 