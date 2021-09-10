from datetime import datetime


class TimeTracker:
    def __init__(self):
        self._times = []
        self._start = self.now()

    def now(self):
        return datetime.now().timestamp() * 1e3

    def reset(self):
        self._start = self.now()
        self._times = []

    def add(self, label):
        self._times.append((label, self.now(), False))

    def show_inline(self, fn=print):
        previous = self._start
        result = ''

        for (label, ts, reset) in self._times + [('Total', self.now(), True)]:
            if len(result):
                result += ' - '
            if reset:
                previous = self._start
            result += '{}: {:.2f} ms'.format(
                label,
                ts - previous
            )
            previous = ts

        fn(result)

    def show(self, indent=0, prefix='', fn=print):
        previous = self._start
        for item in self._times:
            fn('{}{}{}: {:.2f} ms'.format(
                ' ' * indent,
                prefix,
                item[0],
                item[1] - previous,
            ))
            previous = item[1]
