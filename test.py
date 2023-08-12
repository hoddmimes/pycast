import time
import os
import types
import logging
from io import StringIO
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, Future
from concurrent.futures import ThreadPoolExecutor, Future

def test_func() -> :
    ba = bytearray(128)

    return 42, ba

def main():
    ts = test_func()
    print(ts)






if __name__ == '__main__':
    main()