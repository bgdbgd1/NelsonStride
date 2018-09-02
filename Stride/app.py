from flask import Flask, render_template
from data import GetProductsZiengs, GetProductsOmoda
from APIs import GetIndexedSites, GetIndexedBrands, GetProductsForBrand, GetProductDetails, UploadProductsToElastic,\
    DeleteElastic


app = Flask(__name__)

ProductsZiengs = GetProductsZiengs()
ProductsOmoda = GetProductsOmoda()


# Returns the index page.
@app.route('/')
def index():
    return render_template('index.html', products=ProductsZiengs)


@app.route('/omoda')
def omoda():
    return render_template('omoda.html', products=ProductsOmoda)


# API that returns the indexed sites
@app.route('/getIndexedSites', methods=['GET'])
def getIndexedSites():
    return GetIndexedSites()


# API that returns the indexed brands
@app.route('/getIndexedBrands/<string:siteName>', methods=['GET'])
def getIndexedBrands(siteName):
    return GetIndexedBrands(siteName)


# API that returns the products of the provided brand name
@app.route('/getProductsForBrand/<string:siteName>/<string:brand>', methods=['GET'])
def getProductsForBrand(siteName, brand):
    return GetProductsForBrand(siteName, brand)


# API that returns the product details of the provided
@app.route('/getProductDetails/<string:siteName>/<string:productName>', methods=['GET'])
def getProductDetails(siteName, productName):
    return GetProductDetails(siteName, productName)


@app.route('/uploadProductsToElastic/<string:siteName>/', methods=['POST'])
def uploadProductsToElastic(siteName):
    UploadProductsToElastic(siteName)
    if siteName == 'Ziengs':
        return render_template('index.html', products=ProductsZiengs)
    else:
        return render_template('omoda.html', products=ProductsOmoda)


@app.route('/deleteElastic/<string:siteName>/', methods=['POST'])
def deleteElastic(siteName):
    DeleteElastic(siteName)
    if siteName == 'Ziengs':
        return render_template('index.html', products=ProductsZiengs)
    else:
        return render_template('omoda.html', products=ProductsOmoda)


if __name__ == '__main__':
    app.run(debug=True)
