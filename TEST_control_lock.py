import unittest
import RPi.GPIO as GPIO
import mock
import _control_lock
import time
import json

import commands
import pins
import settings


class TestServoControls(unittest.TestCase):

	#region setup and teardown
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
		self._open_patch = mock.patch("__builtin__.open", mock.mock_open(read_data="{}"))
		self.open_mock = self._open_patch.start()

	def tearDown(self):
		self._sleep_patch.stop()
		self._output_patch.stop()
		self._PWM_patch.stop()
		self._setup_patch.stop()
		self._setwarnings_patch.stop()
		self._setmode_patch.stop()
		self._open_patch.stop()
	#endregion

	#region setup mocks
	def test_setup_mocks(self):
		assert self.sleep_mock is time.sleep
		assert self.output_mock is GPIO.output
		assert self.PWM_mock is GPIO.PWM
		assert self.setup_mock is GPIO.setup
		assert self.setwarnings_mock is GPIO.setwarnings
		assert self.setmode_mock is GPIO.setmode
	#endregion

	#region invaild commands
	def test_invalid_command_fails(self):
		with self.assertRaises(NotImplementedError):
			_control_lock.main("BOGUS")
	#endregion

	#region _setup
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
	#endregion

	#region _lock
	@mock.patch("_control_lock._setup", autospec=True)
	def test_lock_output(self, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		# call tag under test
		_control_lock.main(commands.LOCK)
		# test assertions
		self.output_mock.assert_called_once_with(pins.LOCK_STATUS_LED_PIN, GPIO.HIGH)

	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("__main__.MockServo", autospec=True)
	def test_lock_start_stop(self, mock_MockServo, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		assert mock_MockServo is MockServo
		# call tag under test
		_control_lock.main(commands.LOCK)
		# test assertions
		mock_MockServo.return_value.start.assert_called_once_with(settings.SERVO_LOCKED_POSITION)
		mock_MockServo.return_value.stop.assert_called_once_with()

	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("_control_lock._setStateValue", autospec=True)
	def test_lock_setsLockedState(self, mock__setStateValue, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		assert mock__setStateValue is _control_lock._setStateValue
		# call tag under test
		_control_lock.main(commands.LOCK)
		# test assertions
		mock__setStateValue.assert_called_once_with(settings.LOCKED_STATE_KEY, True)
	#endregion

	#region _unlock
	@mock.patch("_control_lock._setup", autospec=True)
	def test_unlock_output(self, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		# call tag under test
		_control_lock.main(commands.UNLOCK)
		# test assertions
		self.output_mock.assert_called_once_with(pins.LOCK_STATUS_LED_PIN, GPIO.LOW)

	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("__main__.MockServo", autospec=True)
	def test_unlock_start_stop(self, mock_MockServo, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		assert mock_MockServo is MockServo
		# call tag under test
		_control_lock.main(commands.UNLOCK)
		# test assertions
		mock_MockServo.return_value.start.assert_called_once_with(settings.SERVO_UNLOCKED_POSITION)
		mock_MockServo.return_value.stop.assert_called_once_with()

	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("_control_lock._setStateValue", autospec=True)
	def test_unlock_setsLockedState(self, mock__setStateValue, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		assert mock__setStateValue is _control_lock._setStateValue
		# call tag under test
		_control_lock.main(commands.UNLOCK)
		# test assertions
		mock__setStateValue.assert_called_once_with(settings.LOCKED_STATE_KEY, False)
	#endregion

	#region _buzz
	@mock.patch("_control_lock._setup", autospec=True)
	def test_buzz_setsOutputHighThenLow(self, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		# call tag under test
		_control_lock.main(commands.BUZZ)
		# test assertions
		calls = [mock.call(pins.BUZZER_PIN, GPIO.HIGH),
				 mock.call(pins.BUZZER_PIN, GPIO.LOW)]
		self.output_mock.assert_has_calls(calls)

	@mock.patch("_control_lock._setup", autospec=True)
	def test_buzz_callsSleep(self, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		# call tag under test
		_control_lock.main(commands.BUZZ)
		# test assertions
		self.sleep_mock.assert_called_once_with(settings.BUZZ_DURATION)
	#endregion

	#region _buzzAndUnlock
	@mock.patch("_control_lock._setup", autospec=True)
	def test_buzzAndUnlock_setsOutputHighThenLow(self, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		# call tag under test
		_control_lock.main(commands.BUZZ_AND_UNLOCK)
		# test assertions
		calls = [mock.call(pins.BUZZER_PIN, GPIO.HIGH),
				 mock.call(pins.BUZZER_PIN, GPIO.LOW)]
		self.output_mock.assert_has_calls(calls)

	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("_control_lock._unlock", autospec=True)
	def test_buzzAndUnlock_callsUnlock(self, mock__unlock, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		assert mock__unlock is _control_lock._unlock
		# call tag under test
		_control_lock.main(commands.BUZZ_AND_UNLOCK)
		# test assertions
		mock__unlock.assert_called_once_with(mock__setup.return_value)

	@mock.patch("_control_lock._setup", autospec=True)
	def test_buzzAndUnlock_callsSleepInOrder(self, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		# call tag under test
		_control_lock.main(commands.BUZZ_AND_UNLOCK)
		# test assertions
		calls = [
			mock.call(settings.BUZZ_DURATION),
			mock.call(settings.SERVO_ROTATION_DURATION),
		]
		self.sleep_mock.assert_has_calls(calls)
	#endregion

	#region _toggleLock
	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("_control_lock._lock", autospec=True)
	@mock.patch("_control_lock._unlock", autospec=True)
	@mock.patch("_control_lock._getStateValue", autospec=True)
	def test_toggleLock_locksWhenNotLocked(self, mock__getStateValue, mock__unlock, mock__lock, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		mock__getStateValue.return_value = False
		# test mocks
		assert mock__setup is _control_lock._setup
		assert mock__lock is _control_lock._lock
		assert mock__unlock is _control_lock._unlock
		assert mock__getStateValue is _control_lock._getStateValue
		# call tag under test
		_control_lock.main(commands.TOGGLE)
		# test assertions
		mock__lock.assert_called_once_with(mock__setup.return_value)
		assert not mock__unlock.called

	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("_control_lock._lock", autospec=True)
	@mock.patch("_control_lock._unlock", autospec=True)
	@mock.patch("_control_lock._getStateValue", autospec=True)
	def test_toggleLock_unlocksWhenLocked(self, mock__getStateValue, mock__unlock, mock__lock, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		mock__getStateValue.return_value = True
		# test mocks
		assert mock__setup is _control_lock._setup
		assert mock__lock is _control_lock._lock
		assert mock__unlock is _control_lock._unlock
		assert mock__getStateValue is _control_lock._getStateValue
		# call tag under test
		_control_lock.main(commands.TOGGLE)
		# test assertions
		mock__unlock.assert_called_once_with(mock__setup.return_value)
		assert not mock__lock.called

	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("_control_lock._lock", autospec=True)
	@mock.patch("_control_lock._unlock", autospec=True)
	@mock.patch("_control_lock._getStateValue", autospec=True, side_effect=KeyError)
	def test_toggleLock_locksOnKeyError(self, mock__getStateValue, mock__unlock, mock__lock, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		assert mock__lock is _control_lock._lock
		assert mock__unlock is _control_lock._unlock
		assert mock__getStateValue is _control_lock._getStateValue
		# call tag under test
		_control_lock.main(commands.TOGGLE)
		# test assertions
		mock__lock.assert_called_once_with(mock__setup.return_value)
		assert not mock__unlock.called
	#endregion

	#region _getStateValue
	def test_getStateValue_goodKey(self):
		# setup
		json_data = '{"locked": false}'
		with mock.patch("__builtin__.open", mock.mock_open(read_data=json_data)) as mock_file:
			# test mock
			assert open(settings.PERSISTENT_STATE_FILE).read() == json_data
			# call tag under test
			locked_state = _control_lock._getStateValue("locked")
			# test assertions
			mock_file.assert_called_with(settings.PERSISTENT_STATE_FILE, "r")
			assert locked_state is False

	def test_getStateValue_badKey(self):
		json_data = '{"locked": false}'
		with mock.patch("__builtin__.open", mock.mock_open(read_data=json_data)) as mock_file:
			# test mock
			assert open(settings.PERSISTENT_STATE_FILE).read() == json_data
			# call tag under test, asserting error raised
			with self.assertRaises(KeyError) as context:
				_control_lock._getStateValue("badKey")
			self.assertTrue("badKey" in context.exception)
	#endregion

	#region _setStateValue
	def test_setStateValue_existingKey(self):
		# setup
		key_to_modify = "locked"
		old_value = False
		new_value = True
		old_json_data = json.dumps({key_to_modify: old_value})
		new_json_data = json.dumps({key_to_modify: new_value})
		assert not old_json_data is new_json_data

		with mock.patch("__builtin__.open", mock.mock_open(read_data=old_json_data)) as mock_file:
			# check mock
			assert open(settings.PERSISTENT_STATE_FILE).read() == old_json_data
			# call tag under test
			_control_lock._setStateValue(key_to_modify, new_value)
			# check open calls
			mock_file.assert_has_calls([mock.call(settings.PERSISTENT_STATE_FILE, "r")])
			mock_file.assert_has_calls([mock.call(settings.PERSISTENT_STATE_FILE, "w")])
			# check write call
			handle = mock_file()
			handle.write.assert_called_once_with(new_json_data)

	def test_setStateValue_newKey(self):
		# setup
		existing_key = "existing key"
		existing_value = "existing value"
		new_key = "new key"
		new_value = "new value"
		assert not existing_key is new_key
		existing_json_data = json.dumps({existing_key: existing_value})
		new_json_data = json.dumps({
			existing_key: existing_value,
			new_key: new_value
		})

		with mock.patch("__builtin__.open", mock.mock_open(read_data=existing_json_data)) as mock_file:
			# check mock
			assert open(settings.PERSISTENT_STATE_FILE).read() == existing_json_data
			# call tag under test
			_control_lock._setStateValue(new_key, new_value)
			# check open calls
			mock_file.assert_has_calls([mock.call(settings.PERSISTENT_STATE_FILE, "r")])
			mock_file.assert_has_calls([mock.call(settings.PERSISTENT_STATE_FILE, "w")])
			# check write call
			handle = mock_file()
			handle.write.assert_called_once_with(new_json_data)
	#endregion

	#region _getStateValue
	@mock.patch("_control_lock._getStateValue", autospec=True, side_effect=KeyError)
	def test_isCurrentlyLocked_FalseOnKeyError(self, mock__getStateValue):
		# setup
		# test mocks
		assert mock__getStateValue is _control_lock._getStateValue
		# call tag under test
		locked = _control_lock._isCurrentlyLocked()
		# test assertions
		assert locked is False

	@mock.patch("_control_lock._getStateValue", autospec=True)
	def test_isCurrentlyLocked_ReturnsTrueWhenTrue(self, mock__getStateValue):
		# setup
		mock__getStateValue.return_value = True
		# test mocks
		assert mock__getStateValue is _control_lock._getStateValue
		# call tag under test
		locked = _control_lock._isCurrentlyLocked()
		# test assertions
		assert locked is True

	@mock.patch("_control_lock._getStateValue", autospec=True)
	def test_isCurrentlyLocked_ReturnsFalseWhenFalse(self, mock__getStateValue):
		# setup
		mock__getStateValue.return_value = False
		# test mocks
		assert mock__getStateValue is _control_lock._getStateValue
		# call tag under test
		locked = _control_lock._isCurrentlyLocked()
		# test assertions
		assert locked is False
	#endregion

	#region _delayLock
	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("_control_lock._unlock", autospec=True)
	def test_delayLock_callsUnlock(self, mock__unlock, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		assert mock__unlock is _control_lock._unlock
		# call tag under test
		_control_lock.main(commands.DELAY_LOCK)
		# test assertions
		mock__unlock.assert_called_once_with(mock__setup.return_value)

	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("_control_lock._lock", autospec=True)
	def test_delayLock_callsLock(self, mock__lock, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		assert mock__lock is _control_lock._lock
		# call tag under test
		_control_lock.main(commands.DELAY_LOCK)
		# test assertions
		mock__lock.assert_called_once_with(mock__setup.return_value)

	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("__main__.MockServo", autospec=True)
	def test_delayLock_callsUnlockThenLock(self, mock_MockServo, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		assert mock_MockServo is MockServo
		# call tag under test
		_control_lock.main(commands.DELAY_LOCK)
		# test assertions
		calls = [
			mock.call(settings.SERVO_UNLOCKED_POSITION),	# first lock
			mock.call(settings.SERVO_LOCKED_POSITION),		# then unlock
		]
		mock_MockServo.return_value.start.assert_has_calls(calls)

	@mock.patch("_control_lock._setup", autospec=True)
	@mock.patch("_control_lock._unlock", autospec=True)
	@mock.patch("_control_lock._lock", autospec=True)
	def test_delayLock_blinksLED(self, mock__lock, mock__unlock, mock__setup):
		# setup
		mock__setup.return_value = MockServo()
		# test mocks
		assert mock__setup is _control_lock._setup
		assert mock__unlock is _control_lock._unlock
		assert mock__lock is _control_lock._lock
		# call tag under test
		_control_lock.main(commands.DELAY_LOCK)
		# test assertions
		calls = []
		for i in range(settings.DELAYED_LOCK_DELAY):
			# blink LED
			calls.append(mock.call(pins.LOCK_STATUS_LED_PIN, GPIO.LOW)) # off
			calls.append(mock.call(pins.LOCK_STATUS_LED_PIN, GPIO.HIGH)) # on

		self.output_mock.assert_has_calls(calls)
	#endregion


class MockServo:
	def start(self, dummy=0):
		pass
	def stop(self):
		pass


if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TestServoControls)
	unittest.TextTestRunner(verbosity=2).run(suite)