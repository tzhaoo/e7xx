# e7xx

A lightweight ctypes wrapper. Wrote it because the PIMikroMove does
not support older E-710 controller, the PITerminal does not work and
PIPython does not support it either, so I wrapped the DLL in Python.
However, the DLL is not included, please get it from PI Software Suite:
https://www.physikinstrumente.com/en/products/software-suite

## Install

```
pip install e7xx
```

## DLL setup

Place `E7XX_GCS_DLL_x64.dll` or `E7XX_GCS_DLL.dll` in the current
working directory of your script.
Python bitness should match the DLL (64-bit Python for x64 DLL).

## Quick start

```python
# Tested on E-710.4CL.

from e7xx import e7xx

with e7xx() as dev:
    dev.connect_rs232(comport=8, baudrate=115200)

    dev.init_axis("1")
    dev.mov("1", 3.0)
    print(dev.qpos("1"))

    dev.mvr("1", 2)
    print(dev.qpos("1"))
```
