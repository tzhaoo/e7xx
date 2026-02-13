import time

from e7xx import e7xx

with e7xx() as dev:
    dev.connect_rs232(comport=8, baudrate=115200)

    dev.init_axis("1")
    dev.mov("1", 6.0)
    time.sleep(0.2)
    print(dev.qpos("1"))

    dev.mvr("1", 1)
    time.sleep(0.2)
    print(dev.qpos("1"))
