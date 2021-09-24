from app.utils.time import TimeTracker
from unittest.mock import Mock, patch


def test_reset():
    tracker = TimeTracker()
    assert len(tracker._times) == 0
    tracker.add('Test #1')
    tracker.add('Test #2')
    tracker.add('Test #3')
    assert len(tracker._times) == 3
    tracker.reset()
    assert len(tracker._times) == 0

def test_add():
    tracker = TimeTracker()
    assert len(tracker._times) == 0
    tracker.add('Test #1')
    tracker.add('Test #2')
    tracker.add('Test #3')
    assert len(tracker._times) == 3
    assert tracker._times[0][0] == 'Test #1'
    assert not tracker._times[0][2]
    assert tracker._times[1][0] == 'Test #2'
    assert not tracker._times[1][2]
    assert tracker._times[2][0] == 'Test #3'
    assert not tracker._times[2][2]

def test_show():
    with patch('app.utils.time.TimeTracker.now', return_value=0):
        tracker = TimeTracker()

    with patch('app.utils.time.TimeTracker.now', return_value=10):
        tracker.add('#1')

    with patch('app.utils.time.TimeTracker.now', return_value=30):
        tracker.add('#2')

    print_mock = Mock()

    with patch('app.utils.time.TimeTracker.now', return_value=50):
        tracker.show_inline(fn=print_mock)

    print_mock.assert_called_with('#1: 10.00 ms - #2: 20.00 ms - Total: 50.00 ms')

    for indent in [0, 2, 4]:
        for prefix in ['', '- ', '# ']:
            print_mock.reset_mock()
            tracker.show(indent=indent, prefix=prefix, fn=print_mock)
            print_mock.assert_any_call('{}{}#1: 10.00 ms'.format(' ' * indent, prefix))
            print_mock.assert_any_call('{}{}#2: 20.00 ms'.format(' ' * indent, prefix))
