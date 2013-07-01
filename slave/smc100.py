from slave.core import Command, InstrumentBase
from slave.types import String, Enum, Integer, Float, Register, Boolean

class SMC100(InstrumentBase):
    def __init__(self, connection, idx=1):
        """
        :param connection: RS-232-C connection to the controller
        :param name: index of the controller on the internal RS-485 link 
        """
        super(SMC100, self).__init__(connection)
        self.idx = idx

        self.errorcode = Command(('TE', String), 
                cfg={'response header separator': 'TE',
                     'program header prefix': self.idx})
        self.enabled = Command(('MM', Boolean), ('MM', Boolean),
                cfg={'response header separator': 'MM', 'program header prefix': self.idx})

        self.state = Command(('TS', String), # should be register, but in hex
                cfg={'response header separator': 'TS',
                     'program header prefix': self.idx})

        self.offset = Command(write=('PR', Float), 
                cfg={'program header prefix': self.idx})

        self.position = Command(('TP', Float), ('PA', Float(min=0)), 
                cfg={'response header separator': 'TP',
                     'program header prefix': self.idx})

        self.set_point = Command(('PH', Float),
                cfg={'response header separator': 'PH',
                     'program header prefix': self.idx})

    def stop(self): self.connection.write('{0}ST'.format(self.idx))
    def enter_configure(self): self.connection.write('{0}PW1'.format(self.idx))
    def load_esp(self, store=2): self.connection.write('{0}ZX{}'.format(self.idx, int(store)))
    def reference(self): self.connection.write('{0}OR'.format(self.idx))
    def exit_configure(self): self.connection.write('{0}PW0'.format(self.idx))
    def reset(self): self.connection.write('{0}RS'.format(self.idx))
