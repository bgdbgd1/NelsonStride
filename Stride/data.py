import json
import re
from collections import namedtuple
from ProductDetails import ProductDetails
from ProductsCategory import ProductsCategory
from elasticsearch import Elasticsearch
import jsonpickle


# Decorator for reading the products from file.
# <param name="func">The function that is executed inside the decorator.
# <param name="fileName">The name of the file that is read.
def getProductsFromFile(func, fileName):
    def wrapper():
        listProductsDetails = []
        listProductsCategories = []
        seenProductName = set()
        with open(fileName) as f:
            content = f.readlines()
            for line in content:
                jsonObject = json.loads(line, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
                # If the json object has the attribute 'page_number', it means that the json object represents
                # a product_listing page. Otherwise, the json object represents a product_details page
                func(jsonObject, listProductsDetails, listProductsCategories, seenProductName)

        # Adds the categories and ranks to the products that they belong to.
        for product in listProductsDetails:
            for category in listProductsCategories:
                for i in range(0, len(category.products)):
                    if product.name == category.products[i]:
                        product.addCategoryAndRank(category.categoryName, (i+1) * category.pageNumber)
        return listProductsDetails
    return wrapper()


# Function that embeds the logic for getting the products from the json object from the Ziengs website.
# <param name="jsonObject">The json object from where the products are extracted.
# <param name="listProductsDetails">The list of products extracted from the json object.
# <param name="listProductsCategories">The list of products categories extracted from the json object.
# <param name="seenProductName">A set that ensures duplicates are removed.
def getProductsZiengs(jsonObject, listProductsDetails, listProductsCategories, seenProductName):
    if hasattr(jsonObject, 'page_number'):
        # Retrieve the products from the HTML body of the product listing pages
        start_sep = '<a title="'
        end_sep = '" class="title"'
        resultListing = []
        tmp = jsonObject.body.split(start_sep)
        for par in tmp:
            if end_sep in par:
                resultListing.append(par.split(end_sep)[0])

        # Remove duplicates of the products from the product listing
        seen = set()
        resultListingUnique = []
        for product in resultListing:
            if product not in seen:
                seen.add(product)
                resultListingUnique.append(product)

        listProductsCategories.append(ProductsCategory(jsonObject.product_category, resultListingUnique,
                                                         jsonObject.page_number))
    else:
        # search for name, brand, color
        startName = '<title> '
        endName = ' | Online'
        resultName = re.search(re.escape(startName) + '(.*)' + re.escape(endName), jsonObject.body).group(1)
        splitResultName = resultName.split(' ')
        if resultName not in seenProductName:
            seenProductName.add(resultName)

            # search for price
            startPrice = '"price" content="'
            endPrice = '" /> </div>'
            resultPrice = re.search(re.escape(startPrice) + '(.*)' + re.escape(endPrice), jsonObject.body).group(1)

            # One product has a brand, a name, a shoe type, a color and a price.
            # The brand can be formed from 1-2 words. If the brand is formed from 2 words, the second word
            # can either start with upper case or lower case.
            # The shoe type can be formed from 1-2 words. If the shoe type is formed from 2 words, the first word
            # starts with upper case and the second word starts with lower case.
            # The following code checks the words in the array in order to determine which of them determine the brand,
            # the shoe type and the color.
            # The splitResultName array has always the element 0 equal to '', so the first word is always found on
            # position one.
            brand = ""
            shoetype = ""
            color = ""
            if splitResultName.__len__() > 3:
                if splitResultName[1][0].islower():
                    brand = splitResultName[0] + " " + splitResultName[1]
                    if splitResultName[3][0].isupper():
                        shoetype = splitResultName[2]
                        color = splitResultName[3]
                    else:
                        shoetype = splitResultName[2] + " " + splitResultName[3]
                        color = splitResultName[4]
                else:
                    if splitResultName[2][0].isupper():
                        brand = splitResultName[0] + " " + splitResultName[1]
                        if splitResultName[3][0].islower():
                            shoetype = splitResultName[2] + splitResultName[3]
                            color = splitResultName[4]
                        else:
                            shoetype = splitResultName[2]
                            color = splitResultName[3]
                    else:
                        brand = splitResultName[0]
                        shoetype = splitResultName[1] + " " + splitResultName[2]
                        color = splitResultName[3]
            elif splitResultName.__len__() == 3:
                brand = splitResultName[0]
                shoetype = splitResultName[1]
                color = splitResultName[2]
            elif splitResultName.__len__() == 2:
                brand = splitResultName[0]
                shoetype = ""
                color = splitResultName[1]
            # Adds a ProductDetails object to the list of ProductDetails objects
            listProductsDetails.append(ProductDetails(brand, resultName, color, shoetype, resultPrice))


# Function that embeds the logic for getting the products from the json object from the Omoda website.
# <param name="jsonObject">The json object from where the products are extracted.
# <param name="listProductsDetails">The list of products extracted from the json object.
# <param name="listProductsCategories">The list of products categories extracted from the json object.
# <param name="seenProductName">A set that ensures duplicates are removed.
def getProductsOmoda(jsonObject, listProductsDetails, listProductsCategories, seenProductName):
    if hasattr(jsonObject, 'page_number'):
        start_sep = '.html" title="'
        end_sep = '" class="artikel-link googleproduct"'
        resultListing = []
        tmp = jsonObject.body.split(start_sep)
        for par in tmp:
            if end_sep in par:
                resultListing.append(par.split(end_sep)[0])

        # Remove duplicates of the products from the product listing
        seen = set()
        resultListingUnique = []
        for product in resultListing:
            if product not in seen:
                seen.add(product)
                resultListingUnique.append(product)

        listProductsCategories.append(ProductsCategory(jsonObject.product_category, resultListingUnique,
                                                         jsonObject.page_number))
    else:
        # search for name, brand, color
        startName = 'name":"'
        endName = '","id'
        startBrand = 'brand":"'
        endBrand = '","category'
        startShoeType = 'category":"'
        endShoeType = '","price'
        startPrice = 'price":"'
        endPrice = '","variant'
        resultName = re.search(re.escape(startName) + '(.*)' + re.escape(endName), jsonObject.body).group(1)
        resultBrand = re.search(re.escape(startBrand) + '(.*)' + re.escape(endBrand), jsonObject.body).group(1)
        resultShoeType = re.search(re.escape(startShoeType) + '(.*)' + re.escape(endShoeType), jsonObject.body).group(1)
        resultPrice = re.search(re.escape(startPrice) + '(.*)' + re.escape(endPrice), jsonObject.body).group(1)
        listProductsDetails.append(ProductDetails(resultBrand, resultName, '', resultShoeType, resultPrice))


ListProductDetailsZiengs = getProductsFromFile(getProductsZiengs, 'crawl_ziengs.jl')
ListProductDetailsOmoda = getProductsFromFile(getProductsOmoda, 'crawl_omoda.jl')


# Returns all products from Ziengs website
def GetProductsZiengs():
    return ListProductDetailsZiengs


# Returns all products from Omoda website
def GetProductsOmoda():
    return ListProductDetailsOmoda
