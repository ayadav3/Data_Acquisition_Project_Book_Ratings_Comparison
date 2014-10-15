

import urllib2
import json
import sys
from datetime import datetime

# NOTE MAX THROTTLE IS 1000


def goodReads_Ratings(isbn_list):


    #isbn_list = ["0441172717", "0141439602"] #sample
    ratingsDict = {}
    for isbn in isbn_list:
        url = "https://www.goodreads.com/book/review_counts.json?isbns="+isbn+"&key=pBii4egUIvDQi7XfR1sCmg"
        request = urllib2.Request(url)


    try:
        page = urllib2.urlopen(request)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print 'Failed to reach url'
            print 'Reason: ', e.reason
            sys.exit()
        elif hasattr(e, 'code'):
            if e.code == 404:
                print 'Error: Invalid ISBN ', e.code
                sys.exit()
            if e.code == '422':
                print 'Error: No ISBN provided ', e.code
                sys.exit()

    page = page.read()

    decoded = page.decode('ASCII', 'ignore')
    book_statistics = json.loads(decoded, strict=False)['books']


    for details in book_statistics:
        isbn = details['isbn']
        average_rating = details['average_rating']
        num_ratings = details['ratings_count']
        ratingsDict[isbn]=average_rating


    return ratingsDict





