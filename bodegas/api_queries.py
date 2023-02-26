import hashlib
import json
from base import app, api, Resource, Flask, request
from flask_jwt_extended import jwt_required
from models import Products

class ProductListResource(Resource, Products):
    @jwt_required()
    def get(self):
        return self.products, 200

class ProductResource(Resource, Products):
    @jwt_required()
    def get(self, pindex, quantity):
        in_stock = self.products[int(pindex)]["quantity"] >= int(quantity)
        result = "Y" if in_stock else "N"
        
        return {"product_id": pindex, "quantity": quantity, "result": result}, 200

api.add_resource(ProductListResource, '/api-queries/products')
api.add_resource(ProductResource, '/api-queries/products/<int:pindex>/<int:quantity>')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')
