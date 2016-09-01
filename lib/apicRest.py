# rewrite apicRest with python requests
# Author: Wei W.
# Time: Dec 16 2015

import json, re, sys, logging, ssl
import requests, urlparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

class apicRest(object):
    def __init__(self, **kwargs):
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.ipAddress = kwargs['ipAddress']
        self.sess = None
        self.token = None

        self.timeout={
            'login'  : 15,
            'logout' : 15,
            'post'   : 15,
            'get'    : 60
        }

        # workaround for ssl validation failure
        ssl._create_default_https_context = ssl._create_unverified_context

    def login(self):
        attributes = {}
        attributes['name'] = self.username
        attributes['pwd'] = self.password

        loginData = {}
        loginData['aaaUser'] = {}
        loginData['aaaUser']['attributes'] = attributes
        loginDataJ = json.dumps(loginData)

        headers = {'connection':'Keep-Alive','Content-Type':''}
        url = 'https://{0}/api/aaaLogin.json'.format(self.ipAddress)
        
        # instantiate requests session
        if self.sess == None:
            self.sess = requests.Session()

        response = self.sess.post(url, data=loginDataJ, verify=False, timeout=self.timeout['login'], headers=headers)

        if response.status_code in [200, 201]:
            logging.info('========= You have successfully login =========')
            
            # show date on apic when login
            logging.info('Login time: {0}'.format(response.headers['date']))
            # show token and timeout value
            content = response.json()
            self.token = content['imdata'][0]['aaaLogin']['attributes']['token']
            logging.info('APIC version: {0}'.format(content['imdata'][0]['aaaLogin']['attributes']['version']))
            logging.info('Build time: {0}'.format(content['imdata'][0]['aaaLogin']['attributes']['buildTime']))
            logging.info('Token: {0}'.format(self.token))
            logging.info('Session timeout: {0} seconds'.format(content['imdata'][0]['aaaLogin']['attributes']['refreshTimeoutSeconds']))
            return self.token
        else:
            logging.error('xxxxxxxxx Login failed (status: {0})xxxxxxxxx'.format(responseStatus))
            return None

    def logout(self):
        attributes = {}
        attributes['name'] = self.username

        logoutData = {}
        logoutData['aaaUser'] = {}
        logoutData['aaaUser']['attributes'] = attributes
        logoutDataJ = json.dumps(logoutData)

        if self.token == None:
            self.login()

        headers = {'Connection':'Keep-Alive','Cookie':'APIC-cookie={0}'.format(self.token)}
        url = 'https://{0}/api/aaaLogout.json'.format(self.ipAddress)

        response = self.sess.post(url, data=loginDataJ, verify=False, timeout=self.timeout['logout'], headers=headers)

        if response.status_code in [200, 201]:
            logging.info('========= You have successfully logout, goodbye! =========')
        else:
            logging.error('xxxxxxxxx Logout failed (status: {0})xxxxxxxxx'.format(responseStatus))

    def post(self, requestData, path, query='', params=''):
        if self.token == None:
            self.login()

        headers = {'Connection':'Keep-Alive','Cookie':'APIC-cookie={0}'.format(self.token)}
        url = { 'scheme'    : 'https',
                'netloc'    : self.ipAddress,
                'path'      : path,
                'query'     : query,
                'params'    : params,
                'fragment'  : ''}
        url = urlparse.ParseResult(**url)
        response = self.sess.post(url.geturl(), data=requestData, verify=False, timeout=self.timeout['post'], headers=headers)

        if response.status_code in [200, 201]:
            return (True, None, None)
        else:
            return (False, response.status_code, response.text.encode('utf-8'))

    def get(self, path, query, params=''):
        if self.token == None:
            self.login()

        headers = {'Connection':'Keep-Alive','Cookie':'APIC-cookie={0}'.format(self.token)}
        url = { 'scheme'    : 'https',
                'netloc'    : self.ipAddress,
                'path'      : path,
                'query'     : query,
                'params'    : params,
                'fragment'  : ''}
        url = urlparse.ParseResult(**url)
        response = self.sess.get(url.geturl(), verify=False, timeout=self.timeout['get'], headers=headers)

        if response.status_code in [200, 201]:
            return (True, None, response.text.encode('utf-8'))
        else:
            return (False, response.status_code, response.text.encode('utf-8'))