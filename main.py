from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]
products_collection = db["products"]
orders_collection = db["orders"]

# Define Product Model
class Product(BaseModel):
    name: str
    price: float
    quantity: int

# Define Order Item Model
class OrderItem(BaseModel):
    product_id: str
    bought_quantity: int
    total_amount: float

# Define User Address Model
class UserAddress(BaseModel):
    city: str
    country: str
    zip_code: str

# Define Order Model
class Order(BaseModel):
    items: list[OrderItem]
    user_address: UserAddress

# Create a new product
@app.post("/products/", response_model=Product)
async def create_product(product: Product):
    product_dict = product.dict()
    inserted_product = products_collection.insert_one(product_dict)
    product_dict["_id"] = str(inserted_product.inserted_id)
    return product_dict

# List all available products
@app.get("/products/", response_model=list[Product])
async def list_products(skip: int = Query(0, description="Skip records"), limit: int = Query(10, description="Limit records")):
    products = list(products_collection.find().skip(skip).limit(limit))
    return products

# Create a new order
@app.post("/orders/", response_model=Order)
async def create_order(order: Order):
    order_dict = order.dict()
    inserted_order = orders_collection.insert_one(order_dict)
    order_dict["_id"] = str(inserted_order.inserted_id)
    return order_dict

# Fetch all orders with pagination
@app.get("/orders/", response_model=list[Order])
async def list_orders(skip: int = Query(0, description="Skip records"), limit: int = Query(10, description="Limit records")):
    orders = list(orders_collection.find().skip(skip).limit(limit))
    return orders

# Fetch a single order by Order ID
@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str = Path(..., description="Order ID")):
    order = orders_collection.find_one({"_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# Update product available quantity
@app.put("/products/{product_id}", response_model=Product)
async def update_product_quantity(product_id: str = Path(..., description="Product ID"), quantity_change: int = Query(..., description="Quantity Change")):
    product = products_collection.find_one({"_id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_quantity = product["product_available_quantity"] + quantity_change
    products_collection.update_one({"_id": product_id}, {"$set": {"product_available_quantity": new_quantity}})
    
    updated_product = products_collection.find_one({"_id": product_id})
    return updated_product
