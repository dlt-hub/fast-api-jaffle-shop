"""
TODO: add pydantic models for jaffle shop
"""

from typing import Optional, List

from pydantic import BaseModel
from datetime import datetime


class Message(BaseModel):
    message: str


class Customer(BaseModel):
    id: str
    name: str


class Supply(BaseModel):
    id: str
    name: str
    cost: float
    perishable: bool
    sku: str


class Item(BaseModel):
    id: str
    order_id: str
    sku: str


class Order(BaseModel):
    id: str
    customer_id: str
    store_id: str
    ordered_at: datetime
    subtotal: float
    tax_paid: float
    order_total: float
    items: Optional[List[Item]]


class Product(BaseModel):
    sku: str
    name: str
    type: str
    price: float
    description: str


class Store(BaseModel):
    id: str
    name: str
    opened_at: datetime
    tax_rate: float
