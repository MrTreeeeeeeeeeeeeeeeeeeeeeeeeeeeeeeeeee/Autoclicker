# Autoclicker

A small Windows autoclicker built in Python.

## Features

- Left-clicks at the current mouse cursor position.
- Configurable delay between clicks.
- Configurable random extra delay.
- Configurable click hold time.
- Global Start / Stop hotkey.
- Global Show menu hotkey.
- Mouse side buttons can be used as hotkeys.
- Modern desktop UI using CustomTkinter.
- Settings saved as JSON.

## Run From Source

Install Python 3.12, then run:

```powershell
python -m pip install -r requirements.txt
python -m autoclicker
```

Default hotkeys:

- Start / Stop: `PgUp`
- Show menu: `PgDn`

To assign a mouse side button, click a hotkey button in the app and press the side button. The app labels these as `Mouse Back` and `Mouse Forward`.

## Settings

Settings are stored at:

```txt
%APPDATA%\Autoclicker\settings.json
```

## Build A Windows EXE

```powershell
.\build_exe.ps1
```

The executable is created at:

```txt
dist\Autoclicker.exe
```

## Tests

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Notes

Global hotkeys can be blocked by apps running with elevated administrator permissions. If hotkeys do not work inside an elevated app, run Autoclicker with matching permissions.
