import hashlib
import json
from base import app, api, Resource, Flask, request
from flask_jwt_extended import jwt_required

class Products():
    products = [
        {"name": "product0", "quantity": 10},
        {"name": "product1", "quantity": 20},
        {"name": "product2", "quantity": 30},
        {"name": "product3", "quantity": 40},
        {"name": "product4", "quantity": 50},
    ]

class ProductListResource(Resource, Products):
    @jwt_required()
    def get(self):
        return self.products, 200

class ProductResource(Resource, Products):
    @jwt_required()
    def get(self, product_id, quantity):
        if (product_id < 0) or (product_id > len(self.products)-1):
            return {"message": f"Product #{product_id} doesn't exists"}, 400
        
        product = self.products[product_id]
        availability = product[quantity] >= quantity
        return {"product_id": product_id, "availability": availability}, 200

api.add_resource(ProductListResource, '/api-queries/products')
api.add_resource(ProductResource, '/api-queries/products/<int:product_id>/<int:quantity>')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')
