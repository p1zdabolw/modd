import os
import sys

from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import QCoreApplication, QTimer

from modd.debugger.runner import Session
from modd.debugger.tracer import TracerBridge

app = QCoreApplication([])
bridge = TracerBridge()
events = {"locations": [], "stacks": [], "locals": [], "output": [], "finished": []}
bridge.location.connect(lambda file, line: events["locations"].append((file, line)))
bridge.stack_changed.connect(events["stacks"].append)
bridge.locals_changed.connect(events["locals"].append)
bridge.output.connect(events["output"].append)
bridge.finished.connect(events["finished"].append)

target = str(Path(__file__).with_name("_debug_target.py"))
source = "x = 1\nbreakpoint()\ny = x + 1\nprint('marker', y)\n"
session = Session(target, source, bridge, True)
session.start()

state = {"seen": 0}


def pump():
    if events["finished"]:
        app.quit()
        return
    if len(events["locations"]) > state["seen"]:
        state["seen"] = len(events["locations"])
        if state["seen"] >= 4:
            session.tracer.request("continue")
        else:
            session.tracer.request("into")
    QTimer.singleShot(15, pump)


QTimer.singleShot(15, pump)
QTimer.singleShot(15000, app.quit)
app.exec()

checks = {
    "stopped_at_breakpoint": len(events["locations"]) >= 3,
    "first_stop_after_bp": events["locations"][0][1] == 3 if events["locations"] else False,
    "marker_output": "marker 2" in "".join(events["output"]),
    "finished_zero": events["finished"] == [0],
    "locals_captured": any("x" in snapshot for snapshot in events["locals"]),
    "stack_captured": len(events["stacks"]) > 0,
}
for name, passed in checks.items():
    print("CHECK", name, "OK" if passed else "FAIL")
print("RESULT", "OK" if all(checks.values()) else "FAIL")
sys.exit(0 if all(checks.values()) else 1)
