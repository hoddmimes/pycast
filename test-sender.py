import random
import time
from pymc.aux.aux import Aux

from pymc.ipmc import IPMC


def getmsg( size:int ) -> bytearray:
    msg = bytearray( size )
    for i in range( size ):
        msg[i] = random.randrange(65,90)
    timstr:str = Aux.time_string()
    msg[:len(timstr)] = bytes(timstr,'utf-8')
    return msg

def callback( data:bytearray, addr):
    msg = data.decode('utf-8')
    print('addr: {} data: {}'.format(addr,msg))

def errorCallback( exception:Exception ):
    print(exception)


def main():
    ipmc = IPMC()
    ipmc.open( '224.10.10.10', 5555)
    ipmc.startReader( callback, errorCallback )
    for i in range(10):
        msg = getmsg(128)
        try:
            ipmc.send( msg )
        except Exception as e:
            print(e)
        time.sleep( 3 )






if __name__ == '__main__':
    main()