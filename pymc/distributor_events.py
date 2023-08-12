from abc import ABC, abstractmethod
from pymc.aux.aux import Aux
from pymc.connection import Connection

class AsyncEvent(ABC):

    def __init__(self, taskName):
        self._taskName = taskName
        super(AsyncEvent,self).__init__()

    @abstractmethod
    def execute(self):
        pass
    def getTaskName(self) -> str:
        return self._taskName






class DistributorEvent(object):
    NAGGING_EXCEPTION = 101
    REMOTE_CONNECTION_CREATED = 102
    REMOTE_CONNECTION_REMOVED = 103
    RETRANSMISSION_NAK = 104
    TOO_MANY_RETRIES = 105
    COMMUNICATION_FAILURE = 106
    CONNECTION_CLOSING = 107

    def __init__(self, event_type:int, message:str = None):
            self.mSignal:int = event_type
            self.mMessage:str = message

    def getMessage(self) -> str:
        return self.mMessage

    def setMessage(self, message:str):
        self.mMessage = message

    def __str__(self):
        return self.mMessage

    def getEventType(self) -> int:
        return self.mSignal

class DistributorErrorEvent(ABC,DistributorEvent):

    def __init__(self, event_type:int, message:str = None):
        super().__init__(event_type, message )



class DistributorCommunicationErrorEvent(DistributorErrorEvent):

    def __init__(self, direction:str, mc_addr:int, mc_port:int, reason:str ):
        super().__init__( DistributorEvent.COMMUNICATION_FAILURE)
        self.mc_addr:str = Aux.ipAddrIntToStr(mc_addr)
        self.mc_port = mc_port

        self.setMessage('{} Connection communication error mc-addr: {} mc-port: {}\n  reason: {} '.format( direction, self.mc_addr, self.mc_port, reason))



class DistributorNaggingErrorEvent(DistributorErrorEvent):

    def __init__(self, mc_addr:int, mc_port:int ):
        super().__init__( DistributorEvent.NAGGING_EXCEPTION)
        self.mc_addr:str = Aux.ipAddrIntToStr(mc_addr)
        self.mc_port:int = mc_port

        super().setMessage('This connection mc-addr: {} mc-port: {} is nagging'.format( self.mc_addr, self.mc_port))


class DistributorNewRemoteConnectionEvent(DistributorEvent):

    def __init__(self, source_addr:int, mc_addr:int, mc_port:int, appl_name:str,
                 appl_id:int, sender_id:int, sender_start_time):
        super().__init__( DistributorEvent.REMOTE_CONNECTION_CREATED)
        self.mc_addr:str = Aux.ipAddrIntToStr(mc_addr)
        self.mc_port:int = mc_port
        self.remote_addr:str = Aux.ipAddrIntToStr(source_addr)
        self.appl_name:str = appl_name
        self.appl_id:int = appl_id
        self.sender_id:int = sender_id
        self.sender_start_time:str = Aux.time_string(sender_start_time)

        self.setMessage("New Remote Connection host: {} mc-addr: {} mc-port: {} Application: {} App-id: {} Sender-id: {} sender started: {}".
                        format(self.remote_addr, self.mc_addr, self.mc_port, self.appl_name, self.sender_id, self.sender_start_time))


class DistributorRemoveRemoteConnectionEvent(DistributorEvent):

    def __init__(self, source_addr:int, mc_addr:int, mc_port:int, appl_name:str,
                 appl_id:int, sender_id:int, sender_start_time):
        super().__init__( DistributorEvent.REMOTE_CONNECTION_REMOVED)
        self.mc_addr:str = Aux.ipAddrIntToStr(mc_addr)
        self.mc_port:int = mc_port
        self.remote_addr:str = Aux.ipAddrIntToStr(source_addr)
        self.appl_name:str = appl_name
        self.appl_id:int = appl_id
        self.sender_id:int = sender_id
        self.sender_start_time:str = Aux.time_string(sender_start_time)

        self.setMessage("Remote Connection Disconnected host: {} mc-addr: {} mc-port: {} Application: {} App-id: {} Sender-id: {} sender started: {}".
                        format(self.remote_addr, self.mc_addr, self.mc_port, self.appl_name, self.sender_id, self.sender_start_time))

class DistributorRetransmissionNAKErrorEvent(DistributorErrorEvent):

    def __init__(self, mc_addr:int, mc_port:int ):
        super().__init__( DistributorEvent.RETRANSMISSION_NAK)
        self.mc_addr:str = Aux.ipAddrIntToStr(mc_addr)
        self.mc_port:int = mc_port

        super().setMessage('Distributor Connection, failed to recover lost message. Message not in remote cache. mc-addr: {} mc-port: {}'.format( self.mc_addr, self.mc_port))


class DistributorTooManyRetransmissionRetriesErrorEvent(DistributorErrorEvent):

    def __init__(self, mc_addr:int, mc_port:int ):
        super().__init__( DistributorEvent.TOO_MANY_RETRIES)
        self.mc_addr:str = Aux.ipAddrIntToStr(mc_addr)
        self.mc_port:int = mc_port

        super().setMessage("Distributor Connection, failed to recover lost message. Too many recovery retries \n. mc-addr: {} mc-port: {}".format( self.mc_addr, self.mc_port))

class DistributorConnectionClosedErrorEvent(DistributorErrorEvent):

    def __init__(self, mc_addr:int, mc_port:int ):
        super().__init__( DistributorEvent.CONNECTION_CLOSING)
        self.mc_addr:str = Aux.ipAddrIntToStr(mc_addr)
        self.mc_port:int = mc_port

        super().setMessage("Distributor Connection Closing mc-addr: {} mc-port: {}".format( self.mc_addr, self.mc_port))


class AsyncEventSignalEvent(AsyncEvent):

    def __init__(self, event: DistributorEvent):
        self.mEvent: DistributorEvent = event

    def execute(self, connection:Connection):
        if connection.isLoggingEnabled( DistributorEvent.e)


@Override


public
void
execute(DistributorConnection
pConnection)
{
if (pConnection.isLogFlagSet(DistributorApplicationConfiguration.LOG_ERROR_EVENTS))
{
if (mEvent instanceof DistributorErrorEvent)
{
    pConnection.log("APPLICATION ERROR EVENT Event: " + mEvent.toString());
}
}

ClientDeliveryController.getInstance().queueEvent(pConnection.mConnectionId, mEvent);
}

@Override


public
String
getTaskName()
{
return this.getClass().getSimpleName();
}

public
String
toString()
{
return "[" + this.getClass().getSimpleName() + "] " + mEvent.toString();
}

}