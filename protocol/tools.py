from typing import Any, Dict, List

from data_models.models import OrderCreationData

# Import the data access layer functions
from db.firestore_client import (
    create_order_db,
    get_order_status_db,
    get_restaurant_menu_db,
    get_user_id_by_email_db,
    search_restaurants_db,
)


def create_tools(mcp):

    @mcp.tool()
    def get_user_id_by_email(email: str) -> str:
        """
        Fetches the user ID for a given email address.

        Args:
            email: The user's email address.

        Returns:
            The user ID as a string, or an error message if not found.
        """
        user_id = get_user_id_by_email_db(email)
        if user_id:
            return user_id
        return f"No user found with email: {email}"

    @mcp.tool()
    def search_restaurants(
        cuisine: str, min_rating: float = 4.0
    ) -> List[Dict[str, Any]]:
        """
        Searches for restaurants based on a specified cuisine and a minimum rating.
        Returns a list of matching restaurants with their key details, including
        name, address, rating, and ID.

        Args:
            cuisine: The type of food to search for (e.g., 'Italian', 'Japanese').
            min_rating: The minimum acceptable rating for a restaurant (e.g., 4.5).
        """
        restaurants = search_restaurants_db(cuisine=cuisine, rating=min_rating)
        if not restaurants:
            return [{"error": "No restaurants found for the specified criteria."}]
        # Convert restaurant objects to dictionaries for the response.
        return [r.to_dict() for r in restaurants]

    @mcp.tool()
    def place_order(
        restaurant_id: str, user_id: str, item_ids: List[str], delivery_address: str
    ) -> str:
        """
        Places a food order at a specific restaurant for a given user. This action
        will create a new order in the system.

        Args:
            restaurant_id: The ID of the restaurant to order from.
            user_id: The ID of the user placing the order.
            item_ids: A list of menu item IDs to be included in the order.
            delivery_address: The full street address for the delivery.

        Returns:
            A confirmation message including the newly created order ID.
        """

        # TODO: confirm restaurant_id, user_id, item_ids exist in the database
        try:
            # Create the main Order object
            new_order = OrderCreationData(
                restaurant_id=restaurant_id,
                user_id=user_id,
                item_ids=item_ids,
                delivery_address=delivery_address,
            )

            order_id = create_order_db(new_order)
        except Exception as e:
            return (
                f"There was an error placing your order. Please try again. "
                f"Technical details: {str(e)}"
            )

        if order_id:
            return f"Order placed successfully! Your order ID is {order_id}."

        return "Failed to place the order. Please check the details and try again."

    @mcp.tool()
    def check_order_status(order_id: str) -> Dict[str, Any]:
        """
        Checks the current status of an existing order using its unique ID and returns
        the status and updated ETA.

        Args:
            order_id: The unique identifier of the order to check.

        Returns:
            A dictionary with the order status and updated ETA (in minutes), or an error
            message if not found.
        """
        from datetime import datetime, timezone

        order_info = get_order_status_db(order_id)
        if not order_info:
            return {
                "error": f"Sorry, I could not find an order with the ID {order_id}."
            }

        status = order_info.get("status")
        created_at = order_info.get("created_at")
        estimated_delivery_time = order_info.get("estimated_delivery_time")

        now = datetime.now(timezone.utc)
        if isinstance(created_at, datetime):
            elapsed_minutes = int((now - created_at).total_seconds() // 60)
        else:
            elapsed_minutes = None

        if estimated_delivery_time is not None and elapsed_minutes is not None:
            updated_eta = max(1, estimated_delivery_time - elapsed_minutes)
        else:
            updated_eta = None

        return {
            "order_id": order_id,
            "status": status,
            "updated_eta_minutes": updated_eta,
        }

    @mcp.tool()
    def get_restaurant_menu(restaurant_id: str) -> List[Dict[str, Any]]:
        """
        Fetches the menu for a specific restaurant identified by its ID.
        The menu is returned as a list of items, each with a name,
        description, and price.
        Args:
            restaurant_id: The unique identifier for the restaurant.
        Returns:
            A list of menu items as dictionaries.
        """
        menu_items = get_restaurant_menu_db(restaurant_id)
        return [item.to_dict() for item in menu_items]
