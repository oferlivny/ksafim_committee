from xml.dom import minidom
import xml.etree.ElementTree as ET
import requests


def clear_tag(e):
    tag=e.tag
    return clear_tag_(tag)

def clear_tag_(tag):
    if "}" in tag: tag=tag.split("}")[1]
    return tag.lower()

def print_formatted(text):
    text=text.replace(","," ")
    text=text.replace("\n","*")
    text = text.replace("\r", "*")
    text=clear_tag_(text)
    try:
        if isinstance(text,str):
            print text.decode('utf-8'),",",
        else:
            print text.encode('utf-8'), ",",
    except:
        print text,",",

def parse_session_item(item):
    baseurl = 'http://knesset.gov.il/Odata/ParliamentInfo.svc/'
    url=baseurl+item
    # print url
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

def work_feed(feed, first=False, test=False):
    next_url=None
    for cc in feed.getchildren():
        if 'entry' not in cc.tag:
            if 'link' in cc.tag:
                if cc.attrib['rel'] == 'next':
                    next_url = cc.attrib['href']
            continue
        if test: print
        "--", cc.tag, cc.text
        for ccc in cc.getchildren():
            if 'link' in ccc.tag:
                if 'KNS_CmtSessionItems' in ccc.attrib.get('title', ''):
                    # print "GOT IT:", ccc.attrib['href']
                    item = parse_session_item(ccc.attrib['href'])
                # print "---", ccc.tag, ccc.text
            if test: print
            "---", ccc.tag, ccc.text
            for cccc in ccc.getchildren():
                if test: print
                "----", cccc.tag, cccc.text
                if first and len(cccc.getchildren()):
                    for ccccc in cccc.getchildren():
                        print_formatted(ccccc.tag)
                    first = False
                    print "Description"
                for ccccc in cccc.getchildren():
                    if ccccc.text:
                        print_formatted(ccccc.text)
                    else:
                        print ",",

                if len(cccc.getchildren()):
                    print_formatted(item.encode('utf_8'))
                    print ""
    return next_url

def process_url(url):
    r = requests.get(url)
    root = ET.fromstring(r.text.encode('utf-8'))
    test = False
    first = True
    for elem in root:
        if test: print
        ">", elem.tag
        if "{" in elem.tag and elem.tag.split("}")[1] == "content":
            print
            "*****"
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
                if test: print
                "-", c.tag, c.text
                if 'feed' not in c.tag:
                    continue

                while (c):
                    next_feed=work_feed(c,first,test)
                    first=False
                    if next_feed:
                        r = requests.get(next_feed)
                        c = ET.fromstring(r.text.encode('utf-8'))
                    else:
                        c = None





url='http://knesset.gov.il/Odata/ParliamentInfo.svc/KNS_Committee(926)?$expand=KNS_CommitteeSessions'
# url='http://knesset.gov.il/Odata/ParliamentInfo.svc/KNS_Committee(926)/KNS_CommitteeSessions'
url=process_url(url)
