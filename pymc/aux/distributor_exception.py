class DistributorTheadExitException(Exception):

    def __init__(self, msg='Thread Exit Interrupt'):
        super().__init__(msg)

class DistributorException( Exception ):
    def __init__(self, message, exception=None):
        self.message = message
        super().__init__( self.message )
        self.system_exception = exception

    def __str__(self):
        if not self.system_exception:
            return self.message
        else:
            _sys_ex = str(self.system_exception)
            _sys_ex_type = type( self.system_exception )
            _sys_ex_name = str( _sys_ex_type.__name__)
            return '{}\n   {}: {}'.format(self.message, _sys_ex_name, _sys_ex)