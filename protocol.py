import json
import pickle
import struct

# ====== 编码 ======
def pack_message(header: dict, payload):
    body = pickle.dumps(payload)

    header["data_size"] = len(body)
    header_bytes = json.dumps(header).encode()

    packet = header_bytes + b"||" + body
    return struct.pack("!I", len(packet)) + packet


# ====== 解码 ======
def recv_all(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("socket closed")
        data += chunk
    return data


def unpack_message(sock):
    raw_len = recv_all(sock, 4)
    (length,) = struct.unpack("!I", raw_len)

    packet = recv_all(sock, length)

    header_raw, body = packet.split(b"||", 1)

    header = json.loads(header_raw.decode())
    payload = pickle.loads(body)

    return header, payload