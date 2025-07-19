from langchain_core.tools import tool
from db_utils import get_db_connection
import json

@tool
def get_menu_items(category: str = None, min_price: float = None, max_price: float = None) -> str:
    """
    Retrieves a list of available menu items, optionally filtered by category and/or price range.
    Returns a JSON string of items, or an empty list if none found.
    
    Args:
        category (str, optional): Filter items by category (e.g., "Hot Drinks", "Pastries").
        min_price (float, optional): Minimum price for items.
        max_price (float, optional): Maximum price for items.

    Example:
    - get_menu_items() -> Get all available items.
    - get_menu_items(category="Hot Drinks") -> Get hot drinks.
    - get_menu_items(min_price=15.0, max_price=25.0) -> Get items between 15 and 25 EGP.
    - get_menu_items(category="Cold Drinks", min_price=18.0) -> Get cold drinks costing 18 EGP or more.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT name, category, price, description FROM menu_items WHERE available = 1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)
        
        if min_price is not None:
            query += " AND price >= ?"
            params.append(min_price)
            
        if max_price is not None:
            query += " AND price <= ?"
            params.append(max_price)
        
        cursor.execute(query, params)
        items = [dict(row) for row in cursor.fetchall()]
        return json.dumps(items, ensure_ascii=False)
    except Exception as e:
        return f"Error retrieving menu items: {e}"
    finally:
        conn.close()
        
@tool
def get_item_details(item_name: str) -> str:
    """
    Retrieves details (name, category, price, description) for a specific menu item.
    Returns a JSON string of the item details, or an empty string if not found.
    Example: get_item_details(item_name="Latte")
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name, category, price, description FROM menu_items WHERE name = ? AND available = 1", (item_name,))
        item = cursor.fetchone()
        return json.dumps(dict(item), ensure_ascii=False) if item else ""
    except Exception as e:
        return f"Error retrieving item details for {item_name}: {e}"
    finally:
        conn.close()
        
@tool
def place_order(customer_session_id: str, items: list[dict]) -> str:
    """
    Records a new order in the database.
    `customer_session_id` should be a unique identifier for the current user session.
    `items` is a list of dictionaries, where each dictionary represents an item in the order:
    `[{"item_name": "Latte", "quantity": 1, "customizations": {"sweetness": "medium", "milk_type": "oat", "temperature": "hot", "size": "large"}}]`
    Returns the order ID if successful, or an error message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Start a transaction
        conn.execute("BEGIN TRANSACTION")

        # Calculate total price and validate items
        total_price = 0.0
        validated_items_data = []
        for item_data in items:
            item_name = item_data.get("item_name")
            quantity = item_data.get("quantity", 1)
            customizations = item_data.get("customizations", {})

            cursor.execute("SELECT id, price FROM menu_items WHERE name = ? AND available = 1", (item_name,))
            menu_item = cursor.fetchone()
            if not menu_item:
                conn.execute("ROLLBACK")
                return f"Error: Item '{item_name}' not found or unavailable."
            
            item_id = menu_item['id']
            item_price = menu_item['price']
            total_price += item_price * quantity
            validated_items_data.append({
                "item_id": item_id,
                "quantity": quantity,
                "customizations": json.dumps(customizations, ensure_ascii=False) # Store customizations as JSON string
            })

        # Insert new order
        cursor.execute("INSERT INTO orders (customer_session_id, total_price) VALUES (?, ?)",
                       (customer_session_id, total_price))
        order_id = cursor.lastrowid

        # Insert order items
        for item_data in validated_items_data:
            cursor.execute('''
                INSERT INTO order_items (order_id, item_id, quantity, customizations)
                VALUES (?, ?, ?, ?)
            ''', (order_id, item_data['item_id'], item_data['quantity'], item_data['customizations']))
        
        conn.execute("COMMIT")
        return f"Order placed successfully! Your Order ID is: {order_id}. Total: {total_price:.2f} EGP."
    except Exception as e:
        conn.execute("ROLLBACK")
        return f"Error placing order: {e}"
    finally:
        conn.close()

@tool
def get_order_status(order_id: int) -> str:
    """
    Retrieves the current status of a specific order.
    Returns a string indicating the status, or an error message if not found.
    Example: get_order_status(order_id=123)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT status, total_price FROM orders WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        if order:
            return f"Order ID {order_id} status: {order['status']}. Total price: {order['total_price']:.2f} EGP."
        else:
            return f"Order ID {order_id} not found."
    except Exception as e:
        return f"Error retrieving order status: {e}"
    finally:
        conn.close()
        
@tool
def cancel_order(order_id: int) -> str:
    """
    Cancels an existing order by updating its status to 'cancelled'.
    Returns a confirmation message or an error if the order cannot be cancelled
    (e.g., already completed or not found).
    Example: cancel_order(order_id=123)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check current status first to prevent cancelling completed orders
        cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
        current_status = cursor.fetchone()

        if not current_status:
            return f"Order ID {order_id} not found."
        
        status = current_status['status']
        if status in ['completed', 'cancelled', 'ready']: # Orders that cannot be cancelled
            return f"Order ID {order_id} cannot be cancelled as its current status is '{status}'."

        cursor.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return f"Order ID {order_id} has been successfully cancelled."
        else:
            return f"Failed to cancel order ID {order_id}." # Should not happen if previous check passed
    except Exception as e:
        return f"Error cancelling order ID {order_id}: {e}"
    finally:
        conn.close()