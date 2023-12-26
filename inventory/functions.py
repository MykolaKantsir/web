from inventory.choices import OrderStatus, orderStatusChangingOrder

# Function to get the next order status
def get_next_order_status(current_order_status):
    try:
        # Find the index of the current status in the changing order list
        current_index = orderStatusChangingOrder.index(current_order_status)

        # Get the next status if the current status is not the last; otherwise, return the same status
        if current_index < len(orderStatusChangingOrder) - 1:
            return orderStatusChangingOrder[current_index + 1]
        else:
            # If current status is the last in the sequence or not in the sequence, return current status
            return current_order_status
    except ValueError:
        # Current order status not in the changing order list, return as 'UNKNOWN' or current status
        return OrderStatus.UNKNOWN

# function to reverse a dict
def reverse_dict(dict):
    return {str(v): k for k, v in dict.items()}
