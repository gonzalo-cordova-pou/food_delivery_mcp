"""
Data models for Food Delivery MCP Server
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from google.cloud.firestore import GeoPoint


@dataclass
class Restaurant:
    """Restaurant data model"""

    id: str
    name: str
    cuisine: str
    address: str
    rating: float
    deliveryFee: float
    estimatedDeliveryTime: int
    subname: Optional[str] = None
    coords: Optional[GeoPoint] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore"""
        data = {
            "id": self.id,
            "name": self.name,
            "cuisine": self.cuisine,
            "address": self.address,
            "rating": self.rating,
            "deliveryFee": self.deliveryFee,
            "estimatedDeliveryTime": self.estimatedDeliveryTime,
        }

        if self.subname:
            data["subname"] = self.subname
        if self.coords:
            data["coords"] = {
                "latitude": self.coords.latitude,
                "longitude": self.coords.longitude,
            }

        return data


@dataclass
class MenuItem:
    """Menu item data model (subcollection of restaurant)"""

    id: str
    name: str
    description: str
    price: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
        }


@dataclass
class User:
    """User data model"""

    id: str
    email: str
    name: str
    order_history: Optional[List[str]] = None

    def __post_init__(self):
        if self.order_history is None:
            self.order_history = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore"""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "orderHistory": self.order_history,
        }


@dataclass
class OrderItem:
    """Order item data model"""

    menu_item_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore"""
        return {
            "menuItemId": self.menu_item_id,
        }


@dataclass
class OrderCreationData:
    """Data required to create a new order"""

    restaurant_id: str
    user_id: str
    item_ids: List[str]
    delivery_address: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore"""
        return {
            "restaurant": self.restaurant_id,
            "user": self.user_id,
            "items": self.item_ids,
            "deliveryAddress": self.delivery_address,
        }


@dataclass
class Order:
    """Order data model"""

    restaurant: str  # Restaurant document reference or ID
    user: str  # User document reference or ID
    items: List[OrderItem]
    delivery_address: str
    status: str = "pending"
    order_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.order_id is None:
            self.order_id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore"""
        data = {
            "restaurant": self.restaurant,
            "user": self.user,
            "items": [item.to_dict() for item in self.items],
            "deliveryAddress": self.delivery_address,
            "status": self.status,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }

        return data


class OrderStatus:
    """Order status constants"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    @classmethod
    def get_valid_statuses(cls) -> List[str]:
        """Get list of valid order statuses"""
        return [
            cls.PENDING,
            cls.CONFIRMED,
            cls.PREPARING,
            cls.READY,
            cls.OUT_FOR_DELIVERY,
            cls.DELIVERED,
            cls.CANCELLED,
        ]


class APIError(Exception):
    """Custom exception for API errors"""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
