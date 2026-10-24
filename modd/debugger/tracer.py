import bdb
import sys
import threading

from PySide6.QtCore import QObject, Signal


class TracerBridge(QObject):
    location = Signal(str, int)
    stack_changed = Signal(list)
    locals_changed = Signal(dict)
    output = Signal(str)
    finished = Signal(int)


class ModdTracer(bdb.Bdb):
    def __init__(self, bridge: TracerBridge, runner_file: str):
        super().__init__()
        self.reset()
        self._bridge = bridge
        self._runner_file = runner_file
        self._resume = threading.Event()
        self._pending = "continue"

    def arm(self):
        frame = sys._getframe().f_back
        self.reset()
        while frame:
            frame.f_trace = self.trace_dispatch
            self.botframe = frame
            frame = frame.f_back
        self.stopframe = self.botframe
        self.returnframe = None
        self.quitting = False
        self.stoplineno = -1
        sys.settrace(self.trace_dispatch)

    def user_line(self, frame):
        if frame.f_code.co_filename == self._runner_file:
            self.set_step()
            return
        self._pause(frame)

    def user_return(self, frame, arg):
        if frame.f_code.co_filename == self._runner_file:
            return
        self._pause(frame)

    def user_exception(self, frame, arg):
        if frame.f_code.co_filename == self._runner_file:
            return
        self._pause(frame)

    def request(self, action):
        self._pending = action
        self._resume.set()

    def interrupt(self):
        self.set_quit()
        self._resume.set()

    def breakpoint_hook(self, *args, **kwargs):
        self.set_trace(sys._getframe().f_back)

    def _pause(self, frame):
        self._resume.clear()
        self._bridge.location.emit(frame.f_code.co_filename, frame.f_lineno)
        self._bridge.stack_changed.emit(self._stack(frame))
        self._bridge.locals_changed.emit(self._snapshot(frame))
        self._resume.wait()
        if self.quitting:
            raise bdb.BdbQuit
        action = self._pending
        self._pending = "continue"
        if action == "over":
            self.set_next(frame)
        elif action == "into":
            self.set_step()
        elif action == "out":
            self.set_return(frame)
        else:
            self.set_continue()

    def _stack(self, frame):
        entries = []
        while frame is not None:
            if frame.f_code.co_filename != self._runner_file:
                entries.append((frame.f_code.co_name, frame.f_code.co_filename, frame.f_lineno))
            frame = frame.f_back
        return entries

    def _snapshot(self, frame):
        values = {}
        for key, value in frame.f_locals.items():
            try:
                values[key] = repr(value)
            except Exception as error:
                values[key] = f"<unavailable: {error}>"
        return values
