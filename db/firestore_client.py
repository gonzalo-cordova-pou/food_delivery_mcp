import sys
from typing import Any, Dict, List, Optional, Set

from dotenv import load_dotenv
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Import the data models to be used for type hinting and instantiation
from data_models.models import MenuItem, OrderCreationData, Restaurant

# Load environment variables from the .env file
load_dotenv()

# Initialize the Firestore client.
# The library automatically uses the GOOGLE_APPLICATION_CREDENTIALS
# environment variable for authentication.
try:
    db = firestore.Client()
    print("Firestore client initialized successfully.", file=sys.stderr)
except Exception as e:
    print(f"Error initializing Firestore client: {e}", file=sys.stderr)
    db = None

# --- Database Functions ---


def search_restaurants_db(cuisine: str, rating: float) -> List[Restaurant]:
    """
    Queries the 'restaurants' collection for documents matching the
    specified cuisine and minimum rating.
    """
    if not db:
        return []
    restaurants_ref = db.collection("restaurants")
    query = restaurants_ref.where(filter=FieldFilter("cuisine", "==", cuisine.lower()))
    query = query.where(filter=FieldFilter("rating", ">=", rating))
    docs = query.stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(Restaurant(**data))
    return results


def get_restaurant_menu_db(restaurant_id: str) -> List[MenuItem]:
    """
    Retrieves all menu items from the 'menu' subcollection
    of a specific restaurant document.
    """
    if not db:
        return []
    menu_items_ref = (
        db.collection("restaurants").document(restaurant_id).collection("menu")
    )
    docs = menu_items_ref.stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(MenuItem(**data))
    return results


def get_order_status_db(order_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a single order document by its ID and returns its status, createdAt, and
    restaurant estimatedDeliveryTime.
    """
    if not db:
        return None
    order_ref = db.collection("orders").document(order_id)
    order_doc = order_ref.get()
    if not order_doc.exists:
        return None
    order_data = order_doc.to_dict()
    status = order_data.get("status")
    created_at = order_data.get("createdAt")
    restaurant_id = order_data.get("restaurant")

    restaurant_ref = db.collection("restaurants").document(restaurant_id)
    restaurant_doc = restaurant_ref.get()
    if not restaurant_doc.exists:
        estimated_delivery_time = None
    else:
        restaurant_data = restaurant_doc.to_dict()
        estimated_delivery_time = restaurant_data.get("estimatedDeliveryTime")

    return {
        "status": status,
        "created_at": created_at,
        "estimated_delivery_time": estimated_delivery_time,
    }


def create_order_db(order_data: OrderCreationData) -> Optional[str]:
    """
    Creates a new document in the 'orders' collection using OrderCreationData.
    """
    if not db:
        return None
    orders_ref = db.collection("orders")
    order_dict = order_data.to_dict()
    # Add server-generated fields
    from datetime import datetime, timezone

    order_dict["status"] = "pending"
    order_dict["createdAt"] = datetime.now(timezone.utc)
    order_dict["updatedAt"] = datetime.now(timezone.utc)
    doc_ref = orders_ref.add(order_dict)[1]
    return doc_ref.id


def get_all_cuisines_db() -> List[str]:
    """
    Retrieves all unique cuisine types from the restaurants collection.
    """
    if not db:
        return []
    docs = db.collection("restaurants").stream()
    cuisines: Set[str] = set()
    for doc in docs:
        data = doc.to_dict()
        if "cuisine" in data:
            cuisines.add(data["cuisine"])
    return sorted(list(cuisines))


def get_user_id_by_email_db(email: str) -> Optional[str]:
    """
    Retrieves the user ID for a given email address.
    """
    if not db:
        return None
    users_ref = db.collection("users")
    query = users_ref.where("email", "==", email).limit(1)
    docs = query.stream()
    for doc in docs:
        return doc.id
    return "No user found with email: {}".format(email)
