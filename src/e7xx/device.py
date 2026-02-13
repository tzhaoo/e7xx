import ctypes
import time

from ._dll import E7XXDll


class E7XXError(RuntimeError):
    def __init__(self, message, code=None, qerr=None):
        super().__init__(message)
        self.code = code
        self.qerr = qerr


class e7xx:
    def __init__(self, dll_path=None):
        self._dll = E7XXDll(dll_path)
        self._id = None

    @property
    def id(self):
        return self._id

    def connect_rs232(self, comport, baudrate):
        self._id = self._dll.dll.E7XX_ConnectRS232(int(comport), int(baudrate))
        if not self._dll.dll.E7XX_IsConnected(self._id):
            self._raise_last_error("ConnectRS232 failed")
        return self._id

    def close(self):
        if self._id is not None:
            self._dll.dll.E7XX_CloseConnection(self._id)
            self._id = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def is_connected(self):
        if self._id is None:
            return False
        return bool(self._dll.dll.E7XX_IsConnected(self._id))

    def init_axis(self, axis):
        self._ensure_connected()
        axis_b = self._axis_bytes(axis)
        self._call_or_raise(self._dll.dll.E7XX_INI, "INI failed", self._id, axis_b)
        on = self._dll.BOOL(1)
        self._call_or_raise(
            self._dll.dll.E7XX_SVO, "SVO failed", self._id, axis_b, ctypes.byref(on)
        )
        self._call_or_raise(self._dll.dll.E7XX_GOH, "GOH failed", self._id, axis_b)
        moving = self._dll.BOOL(1)
        while moving.value:
            self._call_or_raise(
                self._dll.dll.E7XX_IsMoving,
                "IsMoving failed",
                self._id,
                axis_b,
                ctypes.byref(moving),
            )
            time.sleep(0.01)

    def mov(self, axis, target):
        value = ctypes.c_double(float(target))
        self._axis_call(
            axis, self._dll.dll.E7XX_MOV, "MOV failed", ctypes.byref(value)
        )

    def mvr(self, axis, delta):
        value = ctypes.c_double(float(delta))
        self._axis_call(
            axis, self._dll.dll.E7XX_MVR, "MVR failed", ctypes.byref(value)
        )

    def pos(self, axis):
        return self._axis_query_double(axis, self._dll.dll.E7XX_qPOS, "qPOS failed")

    def qpos(self, axis):
        return self.pos(axis)

    def _axis_bytes(self, axis):
        if isinstance(axis, bytes):
            return axis
        return str(axis).encode()

    def _call_or_raise(self, func, prefix, *args):
        if not func(*args):
            self._raise_last_error(prefix)

    def _axis_call(self, axis, func, prefix, *args):
        self._ensure_connected()
        axis_b = self._axis_bytes(axis)
        self._call_or_raise(func, prefix, self._id, axis_b, *args)

    def _axis_query_double(self, axis, func, prefix):
        self._ensure_connected()
        axis_b = self._axis_bytes(axis)
        value = ctypes.c_double(0.0)
        if not func(self._id, axis_b, ctypes.byref(value)):
            self._raise_last_error(prefix)
        return value.value

    def _ensure_connected(self):
        if self._id is None or not self._dll.dll.E7XX_IsConnected(self._id):
            raise E7XXError("Not connected.")

    def _raise_last_error(self, prefix):
        code = self._dll.dll.E7XX_GetError(self._id if self._id is not None else -1)
        msg = self._translate_error(code)
        qerr = self._query_qerr()
        detail = msg or f"e7xx error {code}"
        if qerr not in (None, 0):
            detail = f"{detail} (qERR={qerr})"
        raise E7XXError(f"{prefix}: {detail}", code=code, qerr=qerr)

    def _translate_error(self, code):
        buf = ctypes.create_string_buffer(256)
        ok = self._dll.dll.E7XX_TranslateError(code, buf, ctypes.sizeof(buf))
        if ok:
            return buf.value.decode(errors="replace")
        return None

    def _query_qerr(self):
        err = ctypes.c_int(0)
        ok = self._dll.dll.E7XX_qERR(self._id if self._id is not None else -1, ctypes.byref(err))
        if ok:
            return err.value
        return None
