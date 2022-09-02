from threading import Thread, Timer


class RepeatTimer:
    _cancel = False
    _timer = None

    def __init__(self, seconds, function, *args, **kwargs):
        self.seconds = seconds
        self.function = function
        self.args = args
        self.kwargs = kwargs

        # I added this Thread wrapper because for some reason the Timer was staying alive after the cancel
        # signal. The daemon thread quits when it's the only one running.
        self._thread = Thread(target=self.run, daemon=True)

    def start(self):
        self._thread.start()

    def run(self):
        self._cancel = False
        self._wrapper()

    def cancel(self):
        self._cancel = True
        if self._timer is not None:
            self._timer.cancel()

    def _wrapper(self):
        if not self._cancel:
            self.function(*self.args, **self.kwargs)
            self._timer = Timer(self.seconds, self._wrapper)
            self._timer.start()
