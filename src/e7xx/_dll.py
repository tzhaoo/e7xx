import ctypes
import os


class E7XXDll:
    def __init__(self, dll_path=None):
        if os.name != "nt":
            raise OSError("e7xx is Windows only.")
        self.path = self._find_dll(dll_path)
        self.dll = ctypes.WinDLL(self.path)
        self.BOOL = ctypes.c_int
        self._bind()

    def _find_dll(self, dll_path):
        arch_bits = 64 if ctypes.sizeof(ctypes.c_void_p) == 8 else 32
        dll_names = ["E7XX_GCS_DLL_x64.dll", "E7XX_GCS_DLL.dll"]
        if arch_bits == 32:
            dll_names = ["E7XX_GCS_DLL.dll", "E7XX_GCS_DLL_x64.dll"]

        candidates = []
        if dll_path:
            candidates.append(dll_path)
        env_path = os.getenv("E7XX_DLL_PATH")
        if env_path:
            candidates.append(env_path)

        base_dir = os.path.dirname(__file__)
        cwd = os.getcwd()
        candidates.extend(os.path.join(base_dir, name) for name in dll_names)
        candidates.extend(os.path.join(cwd, name) for name in dll_names)

        for path in candidates:
            if path and os.path.isfile(path):
                return path

        msg = (
            "DLL not found. Set E7XX_DLL_PATH or place "
            "E7XX_GCS_DLL_x64.dll (64-bit) / E7XX_GCS_DLL.dll (32-bit) "
            f"next to the script. Python is {arch_bits}-bit."
        )
        raise FileNotFoundError(msg)

    def _bind(self):
        d = self.dll
        BOOL = self.BOOL

        bindings = [
            ("E7XX_ConnectRS232", [ctypes.c_int, ctypes.c_int], ctypes.c_int),
            ("E7XX_IsConnected", [ctypes.c_int], BOOL),
            ("E7XX_CloseConnection", [ctypes.c_int], None),
            ("E7XX_GetError", [ctypes.c_int], ctypes.c_int),
            ("E7XX_TranslateError", [ctypes.c_int, ctypes.c_char_p, ctypes.c_int], BOOL),
            ("E7XX_qERR", [ctypes.c_int, ctypes.POINTER(ctypes.c_int)], BOOL),
            ("E7XX_INI", [ctypes.c_int, ctypes.c_char_p], BOOL),
            ("E7XX_SVO", [ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(BOOL)], BOOL),
            ("E7XX_GOH", [ctypes.c_int, ctypes.c_char_p], BOOL),
            ("E7XX_IsMoving", [ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(BOOL)], BOOL),
            ("E7XX_MOV", [ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)], BOOL),
            ("E7XX_MVR", [ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)], BOOL),
            ("E7XX_qPOS", [ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double)], BOOL),
        ]
        for name, argtypes, restype in bindings:
            func = getattr(d, name)
            func.argtypes = argtypes
            func.restype = restype
