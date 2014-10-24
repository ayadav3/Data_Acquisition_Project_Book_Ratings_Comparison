
#author: Amit Yadav

import urllib2
import json
import sys
from goodreads import goodReads_Ratings
from amazon_api_final import amazon_ratings


appId = 'Universi-c079-4ab5-89e3-d3ae9e6f8c18'
dataDict = {}

categoryList = ['378'] #Category ids for the category:Non-fiction, fiction, education,,'377','2228'

for category in categoryList:
    isbnDict = {}
    isbn_list = []
    #Url to get all books in the given category
    #Using the Finding API of ebay
    referenceIdUrl = "http://svcs.ebay.com/services/search/FindingService/v1?OPERATION-NAME=findItemsByCategory&SERVICE-VERSION=1.0.0&SECURITY-APPNAME="+appId+"&RESPONSE-DATA-FORMAT=JSON&REST-PAYLOAD&categoryId="+category+"&paginationInput.entriesPerPage=50"
    referenceRequest = urllib2.Request(referenceIdUrl)

    try:
        page = urllib2.urlopen(referenceRequest)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print 'Failed to reach url'
            print 'Reason: ', e.reason
            sys.exit()
        elif hasattr(e, 'code'):
            if e.code == 404:
                print 'Error: Invalid Category Id ', e.code
                sys.exit()
            if e.code == '422':
                print 'Error: No Category Id provided ', e.code
                sys.exit()

    page = page.read()

    decoded = page.decode('ASCII', 'ignore')
    #Extracting book details from the json file
    itemList = json.loads(decoded, strict=False)['findItemsByCategoryResponse'][0]['searchResult'][0]['item']

    #For each book getting the product Id and then the ISBN
    for item in itemList:

        if item.has_key('productId'):
            productId = item['productId'][0]['__value__']
            bookName = item['title'][0]
            #Using the ProductService API of ebay

            productIdUrl = "http://svcs.ebay.com/services/marketplacecatalog/ProductService/v1?OPERATION-NAME=getProductDetails&SERVICE-VERSION=1.3.0&SECURITY-APPNAME="+appId+"&RESPONSE-DATA-FORMAT=JSON&productDetailsRequest.productIdentifier.ePID="+str(productId)
            requestUrl = urllib2.Request(productIdUrl)

            try:
                productPage = urllib2.urlopen(requestUrl)
            except urllib2.URLError, e:
                if hasattr(e, 'reason'):
                    print 'Failed to reach url'
                    print 'Reason: ', e.reason
                    sys.exit()
                elif hasattr(e, 'code'):
                    if e.code == 404:
                        print 'Error: Invalid ISBN ', e.code
                        sys.exit()
            productPage = productPage.read()
            decoded = productPage.decode('ASCII', 'ignore')

            #Extracting details for each product Id
            productDetailsList = json.loads(decoded, strict=False)["getProductDetailsResponse"][0]["product"][0]["productDetails"]

            for productDetail in productDetailsList:
                if productDetail["propertyName"][0] == "ISBN":
                    #Extracting ISBN for each product Id
                    isbn = productDetail["value"][0]["text"][0]["value"][0]
                    isbn_list.append(isbn)

                    #Using the Shopping API of ebay to extract book review ratings
                    reviewUrl = "http://open.api.ebay.com/shopping?callname=FindReviewsAndGuides&responseencoding=JSON&appid="+appId+"&siteid=0&version=531&ProductID.type=ISBN&ProductID.value="+isbn
                    reviewRequest = urllib2.Request(reviewUrl)

                    try:
                        reviewPage = urllib2.urlopen(reviewRequest)
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

                    reviewPage = reviewPage.read()
                    decoded = reviewPage.decode('ASCII', 'ignore')
                    book_statistics = json.loads(decoded, strict=False)

                    if book_statistics['Ack']=='Success':
                        if book_statistics.has_key('ReviewDetails'):
                            if book_statistics['ReviewDetails'].has_key('AverageRating'):
                                rating = book_statistics['ReviewDetails']['AverageRating']
                                isbnDict[isbn] = {"bookTitle": bookName, "ebay_avgRatings": rating}

    goodReads_ratings = goodReads_Ratings(isbn_list)
    amazonRatings = amazon_ratings(isbn_list)
    for key in goodReads_ratings:
        if isbnDict.has_key(key):
            g_rating = goodReads_ratings[key]
            isbnDict[key]["goodreads_avgRatings"] = g_rating
    for key in amazonRatings:
        if isbnDict.has_key(key):
            a_rating = amazonRatings[key]
            isbnDict[key]["amazon_avgRatings"] = a_rating
    dataDict[category] = isbnDict

print dataDict

