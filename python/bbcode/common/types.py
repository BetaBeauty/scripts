
def bytes2str(byte_arr : bytes, encoding="utf-8", **kw) -> str:
    return byte_arr.decode(encoding=encoding, **kw)

def bytes2hex(byte_arr : bytes) -> str:
    return byte_arr.hex()
