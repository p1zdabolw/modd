import bdb
import contextlib
import sys
import threading
import traceback

from modd.debugger.tracer import ModdTracer, TracerBridge


class _Stream:
    def __init__(self, sink):
        self._sink = sink

    def write(self, text):
        self._sink(text)

    def flush(self):
        return None


class Session:
    def __init__(self, path: str, source: str, bridge: TracerBridge, debug: bool):
        self._path = path
        self._source = source
        self._bridge = bridge
        self._debug = debug
        self._tracer = ModdTracer(bridge, __file__) if debug else None
        self._thread = threading.Thread(target=self._execute, daemon=True)

    @property
    def tracer(self):
        return self._tracer

    def start(self):
        self._thread.start()

    def stop(self):
        if self._tracer is not None:
            self._tracer.interrupt()

    def _execute(self):
        code = compile(self._source, self._path, "exec")
        env = {"__name__": "__main__", "__file__": self._path}
        env["breakpoint"] = self._tracer.breakpoint_hook if self._debug else breakpoint
        previous_hook = None
        exit_code = 0
        with contextlib.ExitStack() as streams:
            streams.enter_context(contextlib.redirect_stdout(_Stream(self._bridge.output.emit)))
            streams.enter_context(contextlib.redirect_stderr(_Stream(self._bridge.output.emit)))
            try:
                if self._debug:
                    previous_hook = sys.breakpointhook
                    sys.breakpointhook = self._tracer.breakpoint_hook
                    self._tracer.arm()
                exec(code, env)
            except bdb.BdbQuit:
                exit_code = 0
            except SystemExit as stop:
                exit_code = stop.code if isinstance(stop.code, int) else 1
            except BaseException:
                self._bridge.output.emit(traceback.format_exc())
                exit_code = 1
            finally:
                if self._debug:
                    sys.settrace(None)
                    if previous_hook is not None:
                        sys.breakpointhook = previous_hook
        self._bridge.finished.emit(exit_code)
