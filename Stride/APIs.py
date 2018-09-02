from elasticsearch import Elasticsearch
import json
import jsonpickle
from data import GetProductsOmoda, GetProductsZiengs


# Uploads the indexed products to ElasticSearch.
# <param name="siteName">The name of the website for which data is uploaded.
def UploadProductsToElastic(siteName):
    # Connect to ElasticSearch.
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    # Encode products in JSON format and POST them in ElasticSearch.
    getProducts = []
    if siteName == 'omoda':
        getProducts = GetProductsOmoda()
    else:
        getProducts = GetProductsZiengs()
    for i in range(0, len(getProducts)):
        json_product = jsonpickle.encode(getProducts[i])
        es.index(index='productsdetails' + siteName, doc_type='products', id=i, body=json.loads(json_product))


# Deletes all the products from ElasticSearch
# <param name="siteName">The name of the website for which data is deleted.
def DeleteElastic(siteName):
    # Connect to ElasticSearch.
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    getProducts = []
    if siteName == 'omoda':
        getProducts = GetProductsOmoda()
    else:
        getProducts = GetProductsZiengs()
    for i in range(0, len(getProducts)):
        es.delete(index="productsdetails" + siteName, doc_type="products", id=i)


# Returns the website that was indexed
def GetIndexedSites():
    return jsonpickle.encode({'Sites': [{'www.ziengs.nl'}, {'www.omoda.nl'}]})


# Returns the indexed brands
# <param name="siteName">The name of the website from which the brands are requested.
def GetIndexedBrands(siteName):
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    resultQuery = es.search(index='productsdetails' + siteName, doc_type='products', body={"_source": ["brand"]})
    resultBrands = []
    for hit in resultQuery['hits']['hits']:
        resultBrands.append(hit['_source']['brand'])
    return jsonpickle.encode(resultBrands)


# Returns the product that has the brand name equal to the provided brand name
# <param name="siteName">The name of the website from which the brand is requested.
# <param name="brand">The name of the brand which products are requested.
def GetProductsForBrand(siteName, brand):
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    resultQuery = es.search(index='productsdetails' + siteName, doc_type='products', body={"query": {"match": {"brand": brand}},
                                                                                "_source": ["name"]})
    resultProducts = []
    for hit in resultQuery['hits']['hits']:
        resultProducts.append(hit['_source']['name'])
    return jsonpickle.encode(resultProducts)


# Returns the product and its details that has the product name equal to the provided product name.
# <param name="siteName">The name of the website from which the product is requested.
# <param name="productName">The name of the product for which the details are requested.
def GetProductDetails(siteName, productName):
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    resultQuery = es.search(index='productsdetails' + siteName, doc_type='products', body={"query":
                            {"match_phrase": {"name": productName}}, "_source": ["name", "brand", "color", "shoeType",
                                                                                 "price", "categoryRank"]})
    resultProducts = []
    for hit in resultQuery['hits']['hits']:
        resultProducts.append(hit['_source'])
    return jsonpickle.encode(resultProducts)
