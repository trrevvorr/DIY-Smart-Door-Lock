import RPi.GPIO as GPIO
import time
import threading
import _control_lock

import pins
import commands
import settings

def _setup():
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	# push buttons
	GPIO.setup(pins.TOGGLE_LOCK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(pins.DELAY_LOCK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def _loop():
	while True:
		time.sleep(0.2)
		if GPIO.input(pins.TOGGLE_LOCK_PIN) == False:
			_control_lock.main(commands.LOCK)
		if GPIO.input(pins.DELAY_LOCK_PIN) == False:
			_control_lock.main(commands.UNLOCK)
			time.sleep(15)
			_control_lock.main(commands.LOCK)