# Simplify XML tree by cutting all inrrelavant nodes
# Author: Wei W.
# Time: Feb 11 2016

from lxml import etree

class xTrim(object):
    ''' Use xpath to identify target elements and ancestors in APIC xml config, 
        quickly trim down all irrelevant elements 
        and produce mini xml with a complete tree for target node in each test case.
    '''
    def __init__(self, xconfigs):
            self.srcXmlString = xconfigs 

    def trim(self, tenant, *args):
        ''' Form a mini xml with a complete tree

        Arguments:
        tenant  -- identify a fvTenant tree
        args    -- navigate fvTenant tree and find elements with all tags in args
                    including any ancestor and descendant

        Possible values in args:
            ()                  -- return a fvTenant tree
            ('',[],{},() ...)   -- return a fvTenant tree
            (arg1, '')          -- return a fvTenant tree
            (arg1, fvTenant)    -- return a fvTenant tree
            (arg1)              -- return a mini tree for arg1
            (arg1, arg2, ...)   -- return a mini tree for arg1, arg2, ...

            return None if args are specified but not found

        Exceptions:
            cannot find tenant          -- TypeError
        '''
        srcXml = etree.fromstring(self.srcXmlString)
        rNode = srcXml.xpath('//fvTenant[@name="{0}"]'.format(tenant))
        if not rNode:
            raise TypeError('Cannot find fvTenant: {0}'.format(tenant))
        rNode = rNode[0]

        if not args or 'fvTenant' in args:
            return rNode

        ancestor_and_self_nodes = []
        descendant_nodes = []

        for arg in args:
            if not arg:
                return rNode
            # find all ancestors and self with target nodes
            ancestor_and_self = rNode.xpath('//{0}/ancestor-or-self::*'.format(arg))
            # find all descendant nodes of the target
            descendant = rNode.xpath('//{0}/descendant::*'.format(arg))
            ancestor_and_self_nodes.extend(ancestor_and_self)
            descendant_nodes.extend(descendant)

        # None of the elements is present in configs
        if not ancestor_and_self_nodes:
            return None
        else:
            ancestor_and_self_nodes.extend(descendant_nodes)
        self._recurse_trim(rNode, ancestor_and_self_nodes)
        return rNode


    def _recurse_trim(self, node, referenceList):
        '''Recursively trim down irrelevant children in a node'''
        if len(node) == 0:
            return
        for child in node:
            node.remove(child) if child not in referenceList else self._recurse_trim(child, referenceList)


if __name__ == '__main__':
    main()
