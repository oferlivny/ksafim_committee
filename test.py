#!/bin/python

import xml.etree.ElementTree as ET
import requests

# remove "{...}" stuff
def clear_tag(e):
    tag=e.tag
    return clear_tag_(tag)

# remove "{...}" stuff
def clear_tag_(tag):
    if "}" in tag: tag=tag.split("}")[1]
    return tag.lower()

# print for CSV
# todo: use some native CSV python methods
# todo: print to file instead to stdout
def print_formatted(text):
    text=text.replace(","," ")
    text=text.replace("\n","*")
    text = text.replace("\r", "*")
    text=clear_tag_(text)
    # got some failures in shell for some reason, working around those
    try:
        if isinstance(text,str):
            print text.decode('utf-8'),",",
        else:
            print text.encode('utf-8'), ",",
    except:
        print text,",",

def newline():
    print ""

# get the content of meeting
def parse_session_item(item):
    baseurl = 'http://knesset.gov.il/Odata/ParliamentInfo.svc/'
    url=baseurl+item
    r = requests.get(url)
    root = ET.fromstring(r.text.encode('utf-8'))
    text=""
    for e in root:
        if clear_tag(e)=='entry':
            for ee in e:
                if clear_tag(ee)=='content':
                    for eee in ee:
                        if clear_tag(eee)=='properties':
                            for eeee in eee:
                                if clear_tag(eeee)=='name':
                                    text+= eeee.text + " | "
    return text

# work on a feed.
# note - feed can contain follow up page (next_url).
def work_feed(feed, first=False, debug=False):
    # hold the next page
    next_url=None
    for cc in feed.getchildren():
        # next page is nested here
        if 'entry' not in cc.tag:
            if 'link' in cc.tag:
                if cc.attrib['rel'] == 'next':
                    assert(next_url is None) # just to be sure
                    next_url = cc.attrib['href']
            continue
        if debug: print "--", cc.tag, cc.text
        for ccc in cc.getchildren():
            if 'link' in ccc.tag:
                if 'KNS_CmtSessionItems' in ccc.attrib.get('title', ''):
                    # session description is found in this URL. Process it separately.
                    item = parse_session_item(ccc.attrib['href'])
            if debug: print "---", ccc.tag, ccc.text
            # iterate over sessions.
            for cccc in ccc.getchildren():
                if debug: print "----", cccc.tag, cccc.text
                if first and len(cccc.getchildren()):
                    # print field names. just once - first feed first session.
                    for ccccc in cccc.getchildren():
                        print_formatted(ccccc.tag)
                    first = False
                    print "Description",
                    newline()
                for ccccc in cccc.getchildren():
                    # all session items are interesting. print them all
                    if ccccc.text:
                        print_formatted(ccccc.text)
                    else:
                        print ",",

                if len(cccc.getchildren()):
                    # print last item - session description
                    assert(item is not None)
                    print_formatted(item.encode('utf_8'))
                    newline()

    return next_url

# we start here
def process_url(url):
    r = requests.get(url)
    root = ET.fromstring(r.text.encode('utf-8'))
    # this is ODATA root

    debug = False # debug flag - print everything
    first = True
    for elem in root:
        if debug: print ">", elem.tag

        if clear_tag(elem) == "content":
            # print information about document. this should be last printed lines.
            print "*****"
            for c in elem.getchildren():
                for cc in c.getchildren():
                    if cc.text: print_formatted(cc.tag), print_formatted(cc.text)

        # root
        # # elem
        # # # subelem
        # # # # c
        # # # # # cc - entry/link
        for subelem in elem:
            for c in subelem.getchildren():
                if debug: print "-", c.tag, c.text
                if 'feed' not in c.tag:
                    continue

                # iterate over feeds
                while (c):
                    next_feed=work_feed(c,first,debug)
                    first=False
                    if next_feed:
                        # get next feed
                        r = requests.get(next_feed)
                        c = ET.fromstring(r.text.encode('utf-8'))
                    else:
                        c = None





# todo: add command line
if __name__=='__main__':
    url='http://knesset.gov.il/Odata/ParliamentInfo.svc/KNS_Committee(926)?$expand=KNS_CommitteeSessions'
    # url='http://knesset.gov.il/Odata/ParliamentInfo.svc/KNS_Committee(926)/KNS_CommitteeSessions'
    url=process_url(url)
