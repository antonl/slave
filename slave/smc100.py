from slave.core import Command, InstrumentBase
from slave.types import String, Enum, Integer, Float, Register, Boolean, SingleType, Mapping
from slave.misc import invert_dict

class ErrorAndStateRegister(SingleType):
    '''represents the positioner error and controller state register
    '''
    error_map = {
    	0: 'at negative end-of-run',
        1: 'at positive end-of-run',
        2: 'at peak current limit',
        3: 'at RMS current limit',
        4: 'short-circuit detection',
        5: 'following error',
        6: 'homing time-out',
        7: 'wrong ESP stage',
        8: 'DC voltage too low', 
        9: '80W output power exceeded'
        }

    state_map = {
    	'0A': 'in NOT REFERENCED from RESET',
        '0B': 'in NOT REFERENCED from HOMING',
        '0C': 'in NOT REFERENCED from CONFIGURATION',
        '0D': 'in NOT REFERENCED from DISABLE',
        '0E': 'in NOT REFERENCED from READY',
        '0F': 'in NOT REFERENCED from MOVING',
        '10': 'in NOT REFERENCED from ESP STAGE ERROR', 
        '11': 'in NOT REFERENCED from JOGGING',
        '14': 'in CONFIGURATION',
        '1E': 'in HOMING due to RS-232-C command',
        '1F': 'in HOMING due to SMC-RC command',
        '28': 'in MOVING',
        '32': 'in READY from HOMING',
        '33': 'in READY from MOVING',
        '34': 'in READY from DISABLE',
        '35': 'in READY from JOGGING',
        '3C': 'in DISABLE from READY',
        '3D': 'in DISABLE from MOVING',
        '3E': 'in DISABLE from JOGGING',
        '46': 'in JOGGING from READY',
        '47': 'in JOGGING from DISABLE'
        }

    def __init__(self):
        super(ErrorAndStateRegister, self).__init__(self)
        self._error_reg = Register(invert_dict(ErrorAndStateRegister.error_map))
        self._state_map = Mapping(invert_dict(ErrorAndStateRegister.state_map))

    def __convert__(self, value):
        error_val = self._error_reg.load(value[:4])
        state_val = self._state_map.load(value[4:])
        return (error_val, state_val)

class SMC100CC(InstrumentBase):
    HOME_SEARCH_TYPE = {
    	0: 'mz switch and encoder',
        1: 'current position',
        2: 'mz switch',
        3: 'end-of-range and encoder',
        4: 'end-of-range'}

    def __init__(self, connection, idx=1):
        """
        :param connection: RS-232-C connection to the controller
        :param name: index of the controller on the internal RS-485 link 
        """
        super(SMC100CC, self).__init__(connection)
        self.idx = idx

        cfg = {'program header prefix': str(self.idx), 
               'program header separator': '',
               'response header prefix': str(self.idx),
               'response data separator': ','}

        def merge_cfg(d):
            tmp = d.copy()
            tmp.update(cfg)
            return tmp

        self.errorcode = Command(('TE', String), 
                cfg=merge_cfg({'response header': 'TE'}))
        self.error_string = Command(('TB', String), 
                cfg=merge_cfg({'response header': 'TB'}))


        self.state = Command(('TS', ErrorAndStateRegister),
                cfg=merge_cfg({'response header': 'TS'}))

        self.offset = Command(write=('PR', Float), cfg=cfg)

        self.position = Command(('TP', Float), ('PA', Float(min=0)), 
                cfg=merge_cfg({'response header': 'TP'}))

        self.acceleration = Command(('AC?', Float), ('AC', Float(min=1.e-6, max=1e12)), 
                cfg=merge_cfg({'response header': 'AC'}))


        self.backlash_compensation = Command(('BA?', Float), ('BA', Float(min=0, max=1e12)), 
                cfg=merge_cfg({'response header': 'BA'}))

        self.hysteresis_compensation = Command(('BH?', Float), ('BH', Float(min=0, max=1e12)), 
                cfg=merge_cfg({'response header': 'BH'}))

        self.driver_voltage = Command(('DV?', Float), ('DV', Float(min=12, max=48)), 
                cfg=merge_cfg({'response header': 'DV'}))

        self.kd_lowpass_freqency = Command(('FD?', Float), ('FD', Float(min=1e-6, max=1999.9)), 
                cfg=merge_cfg({'response header': 'FD'}))

        self.following_error_limit = Command(('FE?', Float), ('FE', Float(min=1e-6, max=1e12)), 
                cfg=merge_cfg({'response header': 'FE'}))

        self.friction_compensation = Command(('FF?', Float), ('FF', Float(min=0)), 
                cfg=merge_cfg({'response header': 'FF'}))
        
        #self.stepper_motor_config  # TODO: not implemented
        type1_ = Mapping(invert_dict(SMC100CC.HOME_SEARCH_TYPE))
        self.home_search_type = Command(('HT?', type1_), 
                ('HT', type1_), cfg=merge_cfg({'response header': 'HT'}))

        # Technically, this is a writable command, but not recommended, so not allowed
        self.stage_id = Command(('ID?', String), cfg=merge_cfg({'response header': 'ID'}))

        self.jerk_time = Command(('JR?', Float), ('JR', Float(min=1e-3, max=1e12)), 
                cfg=merge_cfg({'response header': 'JR'}))
        
        self.derivative_gain = Command(('KD?', Float), ('KD', Float(min=0, max=1e12)), 
                cfg=merge_cfg({'response header': 'KD'}))

        self.integral_gain = Command(('KI?', Float), ('KI', Float(min=0, max=1e12)), 
                cfg=merge_cfg({'response header': 'KI'}))
        
        self.proportional_gain = Command(('KP?', Float), ('KP', Float(min=0, max=1e12)), 
                cfg=merge_cfg({'response header': 'KP'}))

        self.velocity_feed_forward = Command(('KV?', Float), ('KV', Float(min=0, max=1e12)), 
                cfg=merge_cfg({'response header': 'KV'}))

        self.enabled = Command(('MM?', Boolean), ('MM', Boolean), 
                cfg=merge_cfg({'response header': 'MM'}))

        self.home_search_velocity = Command(('OH?', Float), ('OH', Float(min=1e-6, max=1e12)), 
                cfg=merge_cfg({'response header': 'OH'}))

        self.home_search_timeout = Command(('OT?', Float), ('OT', Float(min=1, max=1e3)), 
                cfg=merge_cfg({'response header': 'OT'}))

        self.in_configure = Command(('PW?', Boolean), ('PW', Boolean), 
                cfg=merge_cfg({'response header': 'PW'}))

        self.closed_loop = Command(('SC?', Boolean), ('SC', Boolean), 
                cfg=merge_cfg({'response header': 'SC'}))

        self.velocity = Command(('VA?', Float), ('VA', Float(min=1e-6, max=1e12)), 
                cfg=merge_cfg({'response header': 'VA'}))

        self.base_velocity = Command(('VB?', Float), ('VB', Float(min=0)), 
                cfg=merge_cfg({'response header': 'VB'}))

        self.controller_version = Command(('VE', String), 
                cfg=merge_cfg({'response header': 'VE'})) 

        self.esp_profile = Command(('ZX?', String), cfg=merge_cfg({'response header': 'ZX'}))

        # complicated command, TODO
        #self.current_limits = Command(('QI?', Float), ('QI', Float(min=1e-6, max=1e12)), 
        #        cfg=merge_cfg({'response header': 'OH'}))

        self.set_point = Command(('TH', Float),
                cfg=merge_cfg({'response header': 'TH'}))

    def estimate_moving_time(self, rel_offset=1.0): raise NotImplementedError

    def stop(self): self.connection.write('{0}ST'.format(self.idx))
    def enter_configure(self): self.connection.write('{0}PW1'.format(self.idx))
    def load_esp(self, store=2): self.connection.write('{0}ZX{1}'.format(self.idx, int(store)))
    def reference(self): self.connection.write('{0}OR'.format(self.idx))
    def exit_configure(self): self.connection.write('{0}PW0'.format(self.idx))
    def reset(self): self.connection.write('{0}RS'.format(self.idx))
