#!/usr/bin/env python3
import socket
from .misc import stable_rng


def get_free_port(rng=None, low=2000, high=10000):
    if rng is None:
        rng = stable_rng(stable_rng)
    in_use = True
    while in_use:
        port = rng.randint(high - low) + low
        in_use = False
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", port))
        except socket.error as e:
            if e.errno == 98:  # port already in use
                in_use = True
        s.close()
    return port

