# Modd — Mod Development Toolkit

<p align="center">
  <img src="docs/icon.png" width="128" alt="Modd icon">
</p>

Modd is a lightweight desktop workbench for building game mods. It is a single
PySide6 window that combines a project tree, a Python editor with live error
highlighting, a real debugger, and per-game build/deploy adapters. No setup
wizards, no modal popups, no console-diving: everything the tool wants to tell
you appears in the window itself.

## Highlights

- **One predictable window** — project tree on the left, editor and console in
  the middle, Problems and Debugger panels on the right. Every control is
  visible at once; there are no wizards and no hidden steps.
- **In-editor error highlighting** — the editor parses the buffer with `ast`
  400 ms after you stop typing and marks syntax errors with a red wave
  underline plus a tinted line background. The Problems panel lists file,
  line, and message; double-clicking a row opens the file and jumps to the
  line. No modal error dialogs exist anywhere in the application.
- **Built-in debugger** — a `bdb`-based tracer runs your script on a worker
  thread while the UI stays fully responsive. Click the editor gutter to
  toggle a breakpoint, or call `breakpoint()` anywhere in the mod script.
  Step Over / Step Into / Step Out / Continue, a live call stack (double-click
  a frame to open it), and a variables view are always one panel away.
- **Explicit engine adapters** — game support is provided only by pluggy
  plugins, each implementing `detect() / validate() / build() / deploy()`.
  Operations that require a game toolchain that is not installed raise
  `NotImplementedError`, and the problem is reported in the Problems panel —
  by design, never hidden.
- **English and Russian out of the box** — EN/RU toggle buttons sit in the
  toolbar; switching retranslates the whole interface instantly.
- **Dark, non-acid visual theme** — a Tokyo-Night-inspired QSS palette with a
  restrained accent set, plus an application icon drawn entirely in code.

## Supported games

| `game_id`      | Engine / game              | Detected by                                    | Validate               | Build / Deploy                          |
| -------------- | -------------------------- | ---------------------------------------------- | ---------------------- | --------------------------------------- |
| `stalker_xray` | S.T.A.L.K.E.R. (X-Ray)     | `gamedata/` directory or `fsgame.ltx`          | AST check of `mods/main.py` | Needs the game toolchain → reported as unavailable |
| `witcher_red`  | The Witcher 3 (RED engine) | `bin/x64/witcher3.exe` or `mods/` directory    | AST check of `mods/main.py` | Needs the game toolchain → reported as unavailable |
| `unreal`       | Unreal Engine 4/5          | any `*.uproject` file                          | AST check of `mods/main.py` | Needs the game toolchain → reported as unavailable |
| `unity`        | Unity                      | `Assets/` and `ProjectSettings/` directories   | AST check of `mods/main.py` | Needs the game toolchain → reported as unavailable |

Mod projects are engine-agnostic: a `mod.toml` manifest (`name`, `game`) and a
Python entry script `mods/main.py` with a `def apply(ctx)` stub. When a project
is opened, Modd first trusts the `game` field in `mod.toml`, then falls back to
the detection markers above.

## Requirements

- Python **3.11+** (uses `tomllib`)
- PySide6 6.6+ and pluggy 1.3+

```bash
pip install -r requirements.txt
python -m modd.main
```

## Walkthrough

1. **Create Project** — press the toolbar button, fill in a name, pick the
   target game from the adapter registry, and choose a parent folder. Modd
   generates `mod.toml`, `mods/main.py`, and opens the entry script in the
   editor. The folder picker is shown as a non-modal Qt dialog.
2. **Open Project** — point Modd at an existing folder; the adapter is
   detected automatically and shown in the status bar.
3. **Edit** — syntax problems surface in the editor and the Problems panel as
   you type. `Ctrl+S` saves the current file.
4. **Run / Debug** — acts on the currently open `.py` file. stdout and stderr
   of the script are redirected into the Console panel; the exit code is
   reported when it finishes. During debug, breakpoints sync live from all
   open editors, the current line is highlighted in green, and the debugger
   panel shows the call stack and local variables.
5. **Build / Deploy** — always runs validation first; a failed validation
   blocks the operation and lists the problems. Operations that need the
   actual game toolchain raise `NotImplementedError`, which Modd renders in
   the Problems panel as a clear "not available without the game toolchain"
   entry instead of crashing.

## Architecture

```
modd/
├── core/            engine-agnostic contracts
│   ├── hooks.py         pluggy hookspec: get_adapter
│   ├── plugin_manager.py  PluginManager factory + hookimpl marker
│   ├── registry.py      GameRegistry over registered adapters
│   └── game_adapter.py  GameAdapter ABC, ModPackage, entry validation
├── plugins/         one explicit adapter per engine
│   ├── stalker_xray.py  witcher_red.py  unreal.py  unity.py
├── debugger/
│   ├── tracer.py        ModdTracer (bdb.Bdb) + Qt signal bridge
│   └── runner.py        daemon-thread Session with stream redirection
├── ui/
│   ├── main_window.py   toolbar, splitters, sessions, build/deploy flow
│   ├── editor.py        CodeEditor, line numbers, breakpoints, highlighter
│   ├── panels.py        Problems, Debugger, Console panels
│   ├── create_project.py  non-modal project form
│   ├── i18n.py          STRINGS dict (en/ru) + instant retranslate
│   ├── theme.py         dark QSS theme
│   └── icon.py          QPainter logo, runtime QIcon, in-code .ico writer
└── main.py          application entry point
```

Layering rule: `core/` knows nothing about games; `plugins/` know nothing about
the UI; the UI and debugger talk through Qt signals only, so a paused script
never freezes the interface.

## Writing your own adapter

Create a module anywhere, subclass `GameAdapter`, and expose one instance via
the `modd` hook:

```python
from pathlib import Path

from modd.core.game_adapter import GameAdapter, ModPackage
from modd.core.plugin_manager import hookimpl


class MyGameAdapter(GameAdapter):
    game_id = "my_game"
    title = "My Game"

    def detect(self, path: Path) -> bool:
        return (path / "mygame.ini").is_file()

    def validate(self, package: ModPackage) -> list:
        return self.check_python_entry(package)

    def build(self, package: ModPackage) -> Path:
        raise NotImplementedError

    def deploy(self, package: ModPackage) -> Path:
        raise NotImplementedError


@hookimpl
def get_adapter():
    return MyGameAdapter()
```

Register it by adding the module to `BUILTIN_PLUGINS` in `modd/main.py`; it
immediately appears in the Create Project game list and in the detection
rotation. Anything you do not implement should raise `NotImplementedError` —
the UI reports it gracefully.

## Building the single-file .exe

The repository contains `modd.spec` (onefile, windowed) and `build.py`:

```bash
pip install pyinstaller
python build.py
```

`build.py` first re-renders `assets/modd.ico` from the same QPainter code the
app uses at runtime (the ICO container with 16–256 px entries is assembled in
pure Python, so no binary icon assets are committed), then invokes PyInstaller
with `icon="assets/modd.ico"`. The result is `dist/Modd.exe` carrying the Modd
icon instead of the PyInstaller default.

## Development checks

- `python scripts/check_modd.py` — anti-pattern audit: zero comment tokens,
  zero `print`, zero placeholder `pass` / docstring stubs across the package.
- `python scripts/smoke_debugger.py` — headless debugger smoke test
  (breakpoint stop, stepping, locals/stack, console output).
- `python scripts/smoke_ui.py` — headless UI smoke test (adapters, project
  creation, editor tab, run + console, language switch, ICO header).

All smoke tests run under `QT_QPA_PLATFORM=offscreen`.

## Code discipline

The codebase follows a strict fail-fast style: no comments or docstrings, no
`print` debugging, no swallowed exceptions, no placeholder statements.
Unimplemented capability is expressed as `NotImplementedError` and surfaced in
the UI; game support exists only through the explicit adapters listed above.
