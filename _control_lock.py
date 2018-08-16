import RPi.GPIO as GPIO
import time
import threading
import json

import pins
import commands
import settings

def main(action):
	servo = _setup()
	if action == commands.LOCK:
		_lock(servo)
	elif action == commands.UNLOCK:
		_unlock(servo)
	elif action == commands.BUZZ:
		# buzz_thread = threading.Thread(target=_buzz)
		# buzz_thread.start()
		_buzz()
		_unlock(servo)
	elif action == commands.TOGGLE:
		_toggleLock(servo)
	elif action == commands.DELAY_LOCK:
		_delayLock(servo)
	else:
		raise NotImplementedError
	# GPIO.cleanup() # disbled in order to keep LED lit

def _setup():
	# servo
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(pins.SERVO_PIN, GPIO.OUT)
	servo = GPIO.PWM(pins.SERVO_PIN, 50) # 50Hz
	# lock status LED
	GPIO.setup(pins.LOCK_STATUS_LED_PIN, GPIO.OUT)
	# buzzer pin
	GPIO.setup(pins.BUZZER_PIN, GPIO.OUT)
	GPIO.output(pins.BUZZER_PIN,GPIO.LOW)

	return servo

def _lock(servo):
	try:
		servo.start(settings.SERVO_LOCKED_POSITION)
		GPIO.output(pins.LOCK_STATUS_LED_PIN,GPIO.HIGH)
		time.sleep(settings.SERVO_ROTATION_DURATION)
	finally:
		servo.stop()
	_setStateValue(settings.LOCKED_STATE_KEY, True)

def _unlock(servo):
	try:
		servo.start(settings.SERVO_UNLOCKED_POSITION)
		GPIO.output(pins.LOCK_STATUS_LED_PIN,GPIO.LOW)
		time.sleep(settings.SERVO_ROTATION_DURATION)
	finally:
		servo.stop()
	_setStateValue(settings.LOCKED_STATE_KEY, False)

def _buzz():
	try:
		GPIO.output(pins.BUZZER_PIN,GPIO.HIGH) # start buzzing
		time.sleep(settings.BUZZ_DURATION)
	finally:
		GPIO.output(pins.BUZZER_PIN,GPIO.LOW) # end buzzing

def _toggleLock(servo):
	if _isCurrentlyLocked():
		_unlock(servo)
	else:
		_lock(servo)

def _isCurrentlyLocked():
	currently_locked = False
	try:
		currently_locked = _getStateValue(settings.LOCKED_STATE_KEY)
	except KeyError:
		pass # leave currently_locked as default
	return currently_locked

def _getStateValue(key):
	value = None
	with open(settings.PERSISTENT_STATE_FILE, 'r') as f:
		raw_json = f.read()
		persistent_state = json.loads(raw_json)
		value = persistent_state[key]
	return value

def _setStateValue(key, value):
	persistent_state = None
	# load exisiting state
	with open(settings.PERSISTENT_STATE_FILE, 'r') as f:
		raw_json = f.read()
		persistent_state = json.loads(raw_json)
	# set new state
	persistent_state[key] = value
	# save new state
	with open(settings.PERSISTENT_STATE_FILE, 'w') as f:
		raw_json = json.dumps(persistent_state)
		f.write(raw_json)

def _delayLock(servo):
	_unlock(servo)
	time.sleep(settings.DELAYED_LOCK_DELAY)
	_lock(servo)