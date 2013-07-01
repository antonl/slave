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
        cfg = {'program header prefix': str(self.idx), 
               'program header separator': '',
               'response header prefix': str(self.idx)}

        def merge_cfg(d):
            tmp = d.copy()
            tmp.update(cfg)
            return tmp

        self.errorcode = Command(('TE', String), 
                cfg=merge_cfg({'response header': 'TE'}))
        self.error_string = Command(('TB', String), 
                cfg=merge_cfg({'response header': 'TB','response data separator': ''}))

        self.controller_version = Command(('VE', String), 
                cfg=merge_cfg({'response header': 'VE', 'response data separator': ''})) 

        self.enabled = Command(('MM', Boolean), ('MM', Boolean),
                cfg=merge_cfg({'response header': 'MM'}))

        self.state = Command(('TS', String), # should be register, but in hex
                cfg=merge_cfg({'response header': 'TS'}))

        self.offset = Command(write=('PR', Float), cfg=cfg)

        self.position = Command(('TP', Float), ('PA', Float(min=0)), 
                cfg=merge_cfg({'response header': 'TP'}))

        #self.set_point = Command(('PH', Float), # Due to firmware bug, returns something weird
        #        cfg=merge_cfg({'response header': 'PH'}))

    def stop(self): self.connection.write('{0}ST'.format(self.idx))
    def enter_configure(self): self.connection.write('{0}PW1'.format(self.idx))
    def load_esp(self, store=2): self.connection.write('{0}ZX{1}'.format(self.idx, int(store)))
    def reference(self): self.connection.write('{0}OR'.format(self.idx))
    def exit_configure(self): self.connection.write('{0}PW0'.format(self.idx))
    def reset(self): self.connection.write('{0}RS'.format(self.idx))
