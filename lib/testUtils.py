# Test utils to help setup test functions, test data for pytest
# Time: Feb 17 2016
import os, itertools, yaml, urlparse
from xTrim import xTrim
from apicRest import apicRest
from lxml import etree


# test sections
testsection = [ 'MIT',      'LDevVip',
                'CDev',     'Graph',
                'Contract', 'Application',
                'MDevMgr',  'Custom']



def _testdata(testdef, section, trimmer):
    '''Invoke xTrim to generate mini XML tree and modify attributes based on YAML config
    :return: a list of testdata in following format:
            [
                {'tc1' : [tenant, lxml.etree._Element, 'delete']},
                {'tc2' : [tenant, lxml.etree._Element, 'add']},
                {'tc3' : [tenant, lxml.etree._Element, 'delete']},
                ...
            ]
    :rType: list
    '''
    # match operations to functions
    test_operations = { 'add'               : _add,
                        'delete'            : _delete,
                        'addAttribute'      : _addAttr,
                        'deleteAttribute'   : _deleteAttr}

    testdata = []
    for test in testdef[section]:
        testcase = test['test_case']
        tenant = testdef['Common_tenant'] if testcase['common_tenant'] is True else testdef['Tenant']
        testconfig = trimmer.trim(tenant, *testcase['element'])
        sleepTime = testcase['sleep']
        operation = testcase['operation']
        # modify attributes
        if testconfig is not None:
            test_operations[operation](testcase, testconfig)

        testcase = {testcase['id']:[tenant, testconfig, operation, sleepTime]}
        testdata.append(testcase)

    return testdata

def generate_testdata(**kwargs):
    '''Invoked by pytest main program for test data
    :return: a tuple of lists returned by _testdata
    :rType: tuple
    '''
    testdef = kwargs['testdef']
    # get user configs
    xconfigs = _extract_tenant_configs(testdef)
    # instantiate xTrim
    trimmer = xTrim(xconfigs)

    testdata = []

    for section in testsection:
        try:
            testdata.append(_testdata(testdef, section, trimmer))
        except KeyError:
            testdata.append([])

    return tuple(testdata)

def get_APIC(testdef):
    '''Return an APIC object with REST methods
    :rType: object
    '''
    apic = apicRest(ipAddress   = testdef['APIC'],
                    username    = testdef['Username'],
                    password    = testdef['Password'])
    return apic

def _extract_tenant_configs(testdef):
    '''Prepare XML data for xTrim
    :return: XML
    :rType: string
    '''
    tenants = { 'tenant_custom' : testdef['Tenant'],
                'tenant_common' : testdef['Common_tenant']}
    
    query_path = {  'path'  : '/api/class/fvTenant.xml',
                    'query' : 'query-target-filter=or(eq(fvTenant.name,"{tenant_custom}"),eq(fvTenant.name,"{tenant_common}"))&query-target=subtree&rsp-subtree=full&rsp-prop-include=config-only'.format(**tenants),
                    'params': ''}
    # instantiate apic Rest object
    apic = get_APIC(testdef)
    success, stats, response = apic.get(**query_path)
    return response if success is True else None

def _add(testcase, testconfig):
    '''Add status = 'created,modified' to each element in the tree
    :return: None
    '''
    nodes = [testconfig.xpath('//{0}'.format(element)) for element in testcase['element']]
    nodeList = list(itertools.chain(*nodes))
    for node in nodeList:
        node.attrib['status'] = 'created,modified'

def _delete(testcase, testconfig):
    '''Add status = 'deleted' to each element in the tree
    :return: None
    '''
    nodes = [testconfig.xpath('//{0}'.format(element)) for element in testcase['element']]
    nodeList = list(itertools.chain(*nodes))
    for node in nodeList:
        node.attrib['status'] = 'deleted'

def _addAttr(testcase, testconfig):
    '''Assign an attribute value on each target element in the tree
    :return: None
    '''
    attribute = testcase['attribute']
    attrValue = testcase['attrValue']
    nodes = [testconfig.xpath('//{0}'.format(element)) for element in testcase['element']]
    nodeList = list(itertools.chain(*nodes))
    for node in nodeList:
        node.attrib[attribute] = attrValue

def _deleteAttr(testcase, testconfig):
    '''Remove an attribute value on each target element in the tree
    :return: None
    '''
    attribute = testcase['attribute']
    nodes = [testconfig.xpath('//{0}'.format(element)) for element in testcase['element']]
    nodeList = list(itertools.chain(*nodes))
    for node in nodeList:
        node.attrib[attribute] = ''