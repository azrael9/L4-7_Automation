from pyixia import Ixia
from contextlib import contextmanager
from time import sleep

class ixiaStats(object):
    def __init__(self, chassis_ip):
        self.ip = chassis_ip
        self.ixia = Ixia(self.ip)

    def framesSent(self, card, port):
        assert type(card) == int
        assert type(port) == int

        if card <= 0 or port <= 0:
            assert False, 'Invalid number, card {0}, port {1}'.format(card, port)
        try:
            stats = self.ixia.chassis.cards[card - 1].ports[port - 1].stats.frames_sent
        except IndexError:
            assert False, 'Chassis is not connected and discovered! card/port number is out of accpetable range!'
        except:
            raise
        return stats

    def framesReceived(self, card, port):
        assert type(card) == int
        assert type(port) == int

        if card <= 0 or port <= 0:
            assert False, 'Invalid number, card {0}, port {1}'.format(card, port)
        try:
            stats = self.ixia.chassis.cards[card - 1].ports[port - 1].stats.frames_received
        except IndexError:
            assert False, 'Chassis is not connected and discovered or card/port number is out of accpetable range!'
        except:
            raise
        return stats

    def framesSentRate(self, card, port):
        stat_1 = self.framesSent(card, port)
        sleep(5)
        stat_2 = self.framesSent(card, port)
        return (stat_2 - stat_1)/5

    def framesReceivedRate(self, card, port):
        stat_1 = self.framesReceived(card, port)
        sleep(5)
        stat_2 = self.framesReceived(card, port)
        return (stat_2 - stat_1)/5

    @contextmanager
    def connect(self):
        try:
            self.ixia.connect()
            self.ixia.discover()
            yield
            self.ixia.disconnect()
        except:
            raise

    @classmethod
    def isclose(cls, a, b, rel_tol = 0.02, abs_tol = 0):
        '''
        Decide if a and b are relatively close
        rType: boolean
        '''
        return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)