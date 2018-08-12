import unittest
import RPi.GPIO as GPIO
import mock
import _control_lock
import time

import commands
import pins
import settings


class TestServoControls(unittest.TestCase):

	"""
	SETUP AND TEARDOWN
	"""
	def setUp(self):
		self._sleep_patch = mock.patch("time.sleep", autospec=True)
		self.sleep_mock = self._sleep_patch.start()
		self._output_patch = mock.patch("RPi.GPIO.output", autospec=True)
		self.output_mock = self._output_patch.start()
		self._PWM_patch = mock.patch("RPi.GPIO.PWM", autospec=True)
		self.PWM_mock = self._PWM_patch.start()
		self._setup_patch = mock.patch("RPi.GPIO.setup", autospec=True)
		self.setup_mock = self._setup_patch.start()
		self._setwarnings_patch = mock.patch("RPi.GPIO.setwarnings", autospec=True)
		self.setwarnings_mock = self._setwarnings_patch.start()
		self._setmode_patch = mock.patch("RPi.GPIO.setmode", autospec=True)
		self.setmode_mock = self._setmode_patch.start()

	def tearDown(self):
		self._sleep_patch.stop()
		self._output_patch.stop()
		self._PWM_patch.stop()
		self._setup_patch.stop()
		self._setwarnings_patch.stop()
		self._setmode_patch.stop()

	"""
	TEST SETUP MOCKS
	"""
	def test_setup_mocks(self):
		assert self.sleep_mock is time.sleep
		assert self.output_mock is GPIO.output
		assert self.PWM_mock is GPIO.PWM
		assert self.setup_mock is GPIO.setup
		assert self.setwarnings_mock is GPIO.setwarnings
		assert self.setmode_mock is GPIO.setmode

	"""
	TEST INVALID commmands
	"""
	def test_invalid_command_fails(self):
		with self.assertRaises(NotImplementedError):
			_control_lock.main("BOGUS")

	"""
	TESTING _setup
	"""
	@mock.patch("_control_lock._lock", autospec=True)
	def test_setup_setwarnings(self, mock__lock):
		assert mock__lock is _control_lock._lock
		assert self.setwarnings_mock is GPIO.setwarnings
		_control_lock.main(commands.LOCK)
		self.setwarnings_mock.assert_called_once_with(False)


	@mock.patch("_control_lock._lock", autospec=True)
	def test_setup_setmode(self, mock__lock):
		assert mock__lock is _control_lock._lock
		_control_lock.main(commands.LOCK)
		self.setmode_mock.assert_called_once_with(GPIO.BOARD)

	@mock.patch("_control_lock._lock", autospec=True)
	def test_setup_setup(self, mock__lock):
		assert mock__lock is _control_lock._lock
		_control_lock.main(commands.LOCK)
		calls = [mock.call(pins.SERVO_PIN, GPIO.OUT),
				 mock.call(pins.LOCK_STATUS_LED_PIN, GPIO.OUT),
				 mock.call(pins.BUZZER_PIN, GPIO.OUT)]
		self.setup_mock.assert_has_calls(calls, any_order=True)

	@mock.patch("_control_lock._lock", autospec=True)
	def test_setup_PMW(self, mock__lock):
		assert mock__lock is _control_lock._lock
		_control_lock.main(commands.LOCK)
		self.PWM_mock.assert_called_once_with(pins.SERVO_PIN, 50)

	@mock.patch("_control_lock._lock", autospec=True)
	def test_setup_output(self, mock__lock):
		assert mock__lock is _control_lock._lock
		_control_lock.main(commands.LOCK)
		self.output_mock.assert_called_once_with(pins.BUZZER_PIN,GPIO.LOW)

	"""
	TESTING _lock
	"""
	@mock.patch("_control_lock._setup", autospec=True)
	def test_lock_output(self, mock__setup):
		mock__setup.return_value = GPIO.PWM(pins.SERVO_PIN, 50)
		assert mock__setup is _control_lock._setup
		_control_lock.main(commands.LOCK)
		self.output_mock.assert_called_once_with(pins.LOCK_STATUS_LED_PIN, GPIO.HIGH)

	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("__main__.MockServo", autospec=True)
	def test_lock_start_stop(self, mock_MockServo, mock__setup):
		mock__setup.return_value = MockServo()
		assert mock__setup is _control_lock._setup
		assert mock_MockServo is MockServo
		_control_lock.main(commands.LOCK)
		mock_MockServo.return_value.start.assert_called_once_with(settings.SERVO_LOCKED_POSITION)
		mock_MockServo.return_value.stop.assert_called_once_with()

	"""
	TESTING _unlock
	"""
	@mock.patch("_control_lock._setup", autospec=True)
	def test_unlock_output(self, mock__setup):
		mock__setup.return_value = GPIO.PWM(pins.SERVO_PIN, 50)
		assert mock__setup is _control_lock._setup
		_control_lock.main(commands.UNLOCK)
		self.output_mock.assert_called_once_with(pins.LOCK_STATUS_LED_PIN, GPIO.LOW)

	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("__main__.MockServo", autospec=True)
	def test_unlock_start_stop(self, mock_MockServo, mock__setup):
		mock__setup.return_value = MockServo()
		assert mock__setup is _control_lock._setup
		assert mock_MockServo is MockServo
		_control_lock.main(commands.UNLOCK)
		mock_MockServo.return_value.start.assert_called_once_with(settings.SERVO_UNLOCKED_POSITION)
		mock_MockServo.return_value.stop.assert_called_once_with()

	"""
	TESTING _buzz
	"""
	@mock.patch("_control_lock._setup", autospec=True)
	def test_buzz_output(self, mock__setup):
		mock__setup.return_value = GPIO.PWM(pins.SERVO_PIN, 50)
		assert mock__setup is _control_lock._setup
		_control_lock.main(commands.BUZZ)
		calls = [mock.call(pins.BUZZER_PIN, GPIO.HIGH),
				 mock.call(pins.BUZZER_PIN, GPIO.LOW)]
		self.output_mock.assert_has_calls(calls)

class MockServo:
	def start(self, dummy=0):
		pass
	def stop(self):
		pass


if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TestServoControls)
	unittest.TextTestRunner(verbosity=2).run(suite)