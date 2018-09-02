# A class representing a category, together with the products that are part of the category.
class ProductsCategory:
    def __init__(self, categoryName, products, pageNumber):
        self.categoryName = categoryName
        self.products = products
        self.pageNumber = pageNumber
