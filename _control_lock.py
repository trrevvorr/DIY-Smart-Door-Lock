import RPi.GPIO as GPIO
import time
import threading

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
		buzz_thread = threading.Thread(target=_buzz)
		buzz_thread.start()
		_unlock(servo)
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

def _unlock(servo):
	try:
		servo.start(settings.SERVO_UNLOCKED_POSITION)
		GPIO.output(pins.LOCK_STATUS_LED_PIN,GPIO.LOW)
		time.sleep(settings.SERVO_ROTATION_DURATION)
	finally:
		servo.stop()

def _buzz():
	try:
		GPIO.output(pins.BUZZER_PIN,GPIO.HIGH) # start buzzing
		time.sleep(settings.BUZZ_DURATION)
	finally:
		GPIO.output(pins.BUZZER_PIN,GPIO.LOW) # end buzzing

