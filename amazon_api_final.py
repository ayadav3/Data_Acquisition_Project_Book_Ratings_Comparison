


from amazonproduct import API
from lxml import etree
from xml.dom.minidom import parseString
import urllib2
from bs4 import BeautifulSoup
import sys
import re


def amazon_ratings(isbnList):

    AWS_KEY='AKIAJNDBAPB6TLB22AIQ'
    SECRET_KEY='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'
    ASSOCIATE = "schoolproj048-20"

    api = API(AWS_KEY, SECRET_KEY, 'us', ASSOCIATE)

    link = 0
    isbnDict = {}
    for isbn in isbnList:
        books = api.item_lookup(isbn, IdType ='ISBN', SearchIndex = "Books") # give information about the book. we want to pull out link corresponding to the tag <Item>

        dom = parseString(etree.tostring(books))
        item = dom.getElementsByTagName('Item')
        for i in range(0,len(item)):
            if isbn == item[i].childNodes[0].firstChild.nodeValue:
                link = item[i].childNodes[1].firstChild.nodeValue

        #if i.childNodes
        data = dom.getElementsByTagName('ASIN')[0].firstChild.nodeValue

        # Open the URL to get the review data
        Request = urllib2.Request(link)
        try:
            page = urllib2.urlopen(Request)
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                print 'Failed to reach url'
                print 'Reason: ', e.reason
                sys.exit()
            elif hasattr(e, 'code'):
                if e.code == 404:
                    print 'Error: ', e.code
                    sys.exit()

        content = page.read()

        soup = BeautifulSoup(content)

        results = soup.find_all('span', {'class': "reviewCountTextLinkedHistogram noUnderline"})
        for result in results:

            rating = result["title"].split()

            isbnDict[isbn]= rating[0]

    return isbnDict


isbnList = ['0441172717','076243631X', '0141439602']
print amazon_ratings(isbnList)





