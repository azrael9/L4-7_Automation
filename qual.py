# L4-7 device package qualification automation
# Author: Wei W.
# Time: Feb 16, 2016

import os, time, itertools
import pytest, yaml, argparse
from lxml import etree

# autoQual library
from lib.apicRest import apicRest
from lib.testUtils import get_APIC, generate_testdata
from lib.ixiaStats import ixiaStats


# parse arguments for test definition and configs
parser = argparse.ArgumentParser(description = '''Automation test harness''')
parser.add_argument('-t', '--test', required = True, help = 'Mandatory arg - test definition file. Format = "test_xyz.yaml"', nargs = 1, type = str)
parser.add_argument('-i', '--ixia', required = False, help = 'Optional arg - validate ixia traffic', nargs = 1, type = bool)

args = parser.parse_args()
testTemplate = args.test[0]
testTemplate = 'tests/' + testTemplate
# check file existance
if not os.path.isfile(testTemplate):
    raise LookupError('Cannot find following file:\n\t{0}'.format(testTemplate))
# load yaml config
with open(testTemplate,'rbU') as f:
    testdef = yaml.safe_load(f.read())
MIT, LDevVip, CDev, Graph, Contract, Application, MDevMgr, Custom = generate_testdata(testdef=testdef)
apicInfo = dict(APIC = testdef['APIC'], Username = testdef['Username'], Password = testdef['Password'])

# # customize test id
def idfn(val):
    # val is a dict with single key value pair
    if type(val) == dict and len(val) == 1:
        return val.keys()[0]
    else:
        return 'Skipped'

def run(trigger):
    '''
    Main block for execution, this function will be parametrized and called repeatedly
    rType: None
    '''
    # Begin "POST" trigger
    tenant, config, operation, sleeptime = tuple(itertools.chain(*trigger.values()))
    # xTrim returns None if target element not found
    if config == None or len(config) == 0:
        pytest.skip("Test object(element) not found in user configs")

    post_config = etree.tostring(config)
    post = {'path'          : 'api/node/mo/.xml',
            'requestData'   : post_config}
    apic = get_APIC(apicInfo)
    success, status, error = apic.post(**post)
    if not success:
        pytest.fail('Apic POST failed with status[{0}] and error message: {1}'.format(status, error))
    
    time.sleep(sleeptime)
    
    # Traffic validation
    if args.ixia[0] == True and operation == 'add':
        ixia = ixiaStats(testdef['Ixia'])
        with ixia.connect():
            framesTxRate = ixia.framesSentRate(testdef['TxCard'], testdef['TxPort'])
            framesRxRate = ixia.framesReceivedRate(testdef['RxCard'], testdef['RxPort'])
        if not ixia.isclose(framesTxRate, framesRxRate) or ixia.isclose(framesTxRate, 0):
            pytest.fail('Ixia traffic validation failed! Tx rate: {0}  Rx rate: {1}'.format(framesTxRate, framesRxRate))


@pytest.mark.skipif(not MIT, reason='MIT test section not specified')
@pytest.mark.parametrize("trigger", MIT, ids=idfn)
def test_MIT(trigger):
    '''test section: MIT'''
    run(trigger)

@pytest.mark.skipif(not LDevVip, reason='LDevVip test section not specified')
@pytest.mark.parametrize("trigger", LDevVip, ids=idfn)
def test_LDevVip(trigger):
    '''test section: LDevVip'''
    run(trigger)

@pytest.mark.skipif(not CDev, reason='CDev test section not specified')
@pytest.mark.parametrize("trigger", CDev, ids=idfn)
def test_CDev(trigger):
    '''test section: CDev'''
    run(trigger)

@pytest.mark.skipif(not Graph, reason='Graph test section not specified')
@pytest.mark.parametrize("trigger", Graph, ids=idfn)
def test_Graph(trigger):
    '''test section: Graph'''
    run(trigger)

@pytest.mark.skipif(not Contract, reason='Contract test section not specified')
@pytest.mark.parametrize("trigger", Contract, ids=idfn)
def test_Contract(trigger):
    '''test section: Contract'''
    run(trigger)

@pytest.mark.skipif(not Application, reason='Application test section not specified')
@pytest.mark.parametrize("trigger", Application, ids=idfn)
def test_Application(trigger):
    '''test section: Application'''
    run(trigger)

@pytest.mark.skipif(not MDevMgr, reason='MDevMgr test section not specified')
@pytest.mark.parametrize("trigger", MDevMgr, ids=idfn)
def test_MDevMgr(trigger):
    '''test section: MDevMgr'''
    run(trigger)

@pytest.mark.skipif(not Custom, reason='Custom test section not specified')
@pytest.mark.parametrize("trigger", Custom, ids=idfn)
def test_Custom(trigger):
    '''test section: Custom'''
    run(trigger)    


def main():
    pytest.main('-rxs')

if __name__ == '__main__':
    main()
