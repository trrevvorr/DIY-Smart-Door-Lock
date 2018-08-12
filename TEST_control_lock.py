import unittest
import RPi.GPIO as GPIO
import mock
import _control_lock

import commands
import pins
import settings


class TestStringMethods(unittest.TestCase):

	"""
	SETUP AND TEARDOWN
	"""
	def setUp(self):
		self.sleep_patch = mock.patch("time.sleep", autospec=True)
		self.sleep_patch.start()

	def tearDown(self):
		self.sleep_patch.stop()

	def test_invalid_command_fails(self):
		with self.assertRaises(NotImplementedError):
			_control_lock.main("BOGUS")

	"""
	TESTING _setup
	"""
	@mock.patch("RPi.GPIO.setwarnings", autospec=True)
	@mock.patch("_control_lock._lock", autospec=True)
	def test_setup_setwarnings(self, mock__lock, mock_setwarnings):
		assert mock__lock is _control_lock._lock
		assert mock_setwarnings is GPIO.setwarnings
		_control_lock.main(commands.LOCK)
		mock_setwarnings.assert_called_once_with(False)


	@mock.patch("RPi.GPIO.setmode", autospec=True)
	@mock.patch("_control_lock._lock", autospec=True)
	def test_setup_setmode(self, mock__lock, mock_setmode):
		assert mock__lock is _control_lock._lock
		assert mock_setmode is GPIO.setmode
		_control_lock.main(commands.LOCK)
		mock_setmode.assert_called_once_with(GPIO.BOARD)

	@mock.patch("RPi.GPIO.setup", autospec=True)
	@mock.patch("_control_lock._lock", autospec=True)
	def test_setup_setup(self, mock__lock, mock_setup):
		assert mock__lock is _control_lock._lock
		assert mock_setup is GPIO.setup
		_control_lock.main(commands.LOCK)
		calls = [mock.call(pins.SERVO_PIN, GPIO.OUT),
				 mock.call(pins.LOCK_STATUS_LED_PIN, GPIO.OUT),
				 mock.call(pins.BUZZER_PIN, GPIO.OUT)]
		mock_setup.assert_has_calls(calls, any_order=True)

	@mock.patch("RPi.GPIO.PWM", autospec=True)
	@mock.patch("_control_lock._lock", autospec=True)
	def test_setup_PMW(self, mock__lock, mock_PWM):
		assert mock__lock is _control_lock._lock
		assert mock_PWM is GPIO.PWM
		_control_lock.main(commands.LOCK)
		mock_PWM.assert_called_once_with(pins.SERVO_PIN, 50)

	@mock.patch("RPi.GPIO.output", autospec=True)
	@mock.patch("_control_lock._lock", autospec=True)
	def test_setup_output(self, mock__lock, mock_output):
		assert mock__lock is _control_lock._lock
		assert mock_output is GPIO.output
		_control_lock.main(commands.LOCK)
		mock_output.assert_called_once_with(pins.BUZZER_PIN,GPIO.LOW)

	"""
	TESTING _lock
	"""
	@mock.patch("RPi.GPIO.output", autospec=True)
	@mock.patch("_control_lock._setup", autospec=True)
	def test_lock_output(self, mock__setup, mock_output):
		mock__setup.return_value = GPIO.PWM(pins.SERVO_PIN, 50)
		assert mock__setup is _control_lock._setup
		assert mock_output is GPIO.output
		_control_lock.main(commands.LOCK)
		mock_output.assert_called_once_with(pins.LOCK_STATUS_LED_PIN, GPIO.HIGH)

	@mock.patch("RPi.GPIO.output", autospec=True)
	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("__main__.MockServo", autospec=True)
	# @mock.patch("__main__.MockServo.stop", autospec=True)
	def test_lock_start_stop(self, mock_MockServo, mock__setup, mock_output):
		mock__setup.return_value = MockServo()
		assert mock__setup is _control_lock._setup
		assert mock_output is GPIO.output
		assert mock_MockServo is MockServo
		# assert mock_stop is MockServo.stop
		_control_lock.main(commands.LOCK)
		mock_MockServo.return_value.start.assert_called_once_with(settings.SERVO_LOCKED_POSITION)
		mock_MockServo.return_value.stop.assert_called_once_with()



class MockServo:
	def start(self, dummy=0):
		pass
	def stop(self):
		pass


if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TestStringMethods)
	unittest.TextTestRunner(verbosity=2).run(suite)