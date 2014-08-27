#!/usr/bin/env python

import logging
import mechanize
import os, sys
from BeautifulSoup import BeautifulSoup
from pushbullet import PushBullet

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def login(u,p):
    global log
    
    br = mechanize.Browser()
    log.info("LOGIN: Accessing page")
    r = br.open('https://goes-app.cbp.dhs.gov/main/goes')
    
    log.info("LOGIN: Logging in")
    br.form = br.forms().next()
    br.form.controls[0].value = u
    br.form.controls[1].value = p
    r = br.submit()

    log.info("LOGIN: Fetching status page")
    r = br.follow_link(br.find_link(text='Enter'))

    return r.read()
    
def getstatus(html):
    global log
    
    log.info("PARSE: Parsing status page")
    parser = BeautifulSoup(html)
    
    appinfo = parser.findAll('div', attrs={'class': 'appcontent'})[0].findAll('tr', attrs={'class': 'gridItem'})[0].findAll('td')
    appid = appinfo[0].text[0:10].strip()
    status = appinfo[4].text.replace("&nbsp;", "")

    return (appid, status)
    
def currentstatus():
    name = os.path.join(here, "appstatus.txt")
    try:
        with open(name) as f:
            status = f.readlines()[0].split(",")
        f.closed
    except:        
        f = open(name, "w")
        f.close()
        status = None
    finally:
        return status    
        
def writestatus(status):
    name = os.path.join(here, "appstatus.txt")
    with open(name, 'w') as f:
        f.write( ",".join(status) )
        
def main(u,p):
    global log
    
    PB_KEY = "Put your PushBullet API key here."
    PB_EMAIL = "Put your PushBullet account email here."
    
    local_status = currentstatus()
    official_status = getstatus(login(u,p))
    # No local status = first run, initialize
    if not local_status:
        log.info("First run, writing status.")
        writestatus(official_status)
        return False
    else:    
        if local_status[1] != official_status[1]:
            pb = PushBullet(PB_KEY)
            
            body = "Application #{}: {}".format(*official_status)
            # Push
            data = dict(type='note', 
                        title='Your Global Entry application has updated', 
                        body=body,
                        email=PB_EMAIL)
            ok, resp = pb._push(data)
            log.info("PUSH: updated status {}".format(body))
            if not ok:
                log.error(resp)
        else:
            log.info("PUSH: Status remained the same, not pushing.")        
    
if __name__ == '__main__':
    U = "username"
    P = "password"
    here = os.path.dirname(os.path.realpath(sys.argv[0]))
        
    main(U,P)
