# XQEMU-Manager Prototype

| Windows Build Status |
| -------------------- |
| [![Build status](https://ci.appveyor.com/api/projects/status/9hb88yawy54b0086/branch/master?svg=true)](https://ci.appveyor.com/project/xqemu-bot/xqemu-manager?branch=master) |
| [Latest Build](https://ci.appveyor.com/api/projects/xqemu-bot/xqemu-manager/artifacts/xqemu-manager.zip?branch=master&pr=false) |

This is a helper GUI prototype (hastily hacked together) to launch and control
[XQEMU](http://github.com/xqemu/xqemu), currently in very early stages. Pull
requests welcome.

# How it works

Basically this is just a GUI to construct the command line arguments passed
to XQEMU. Settings are saved to a simple .json file, and loaded again at
startup.

Why not integrate into XQEMU directly? The approach used here is less invasive
and works "well enough" for this purpose. XQEMU can also be controlled directly
at runtime through the QMP interface, so additional features (eject dvd for
instance) can be added to this.

## How to use it

Depends on PyQt5, available with pip. Then run like:

```
pip install PyQt5
python main.py
```
