from CategoryRank import CategoryRank

# A class representing a product and its details.
class ProductDetails:
    def __init__(self, brand, name, color, shoetype, price):
        self.brand = brand
        self.name = name
        self.color = color
        self.shoeType = shoetype
        self.price = price
        self.categoryRank = []


# Adds the category array and its corresponding rank to the categoryRank list
    def addCategoryAndRank(self, category, rank):
        self.categoryRank.append(CategoryRank(category, rank))

# Returns a string containing the categories and the corresponding ranks of a product.
    def toStringCategory(self):
        result = ''
        resultCategory = 'Category: '
        for categoryRank in self.categoryRank:
            for category in categoryRank.category:
                resultCategory += category + ' '
            result += resultCategory + " Rank: " + str(categoryRank.rank)
            resultCategory = ("<br>Category: ")
        return result
