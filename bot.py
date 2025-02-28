from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import csv
import os

app = Flask(__name__)

# Temporary storage for customer data (use database for production)
customer_data = {}

# File path for the CSV file
CSV_FILE = "customer_data.csv"

# Initialize the CSV file (create if it doesn't exist)
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Phone Number", "State", "Item", "Quantity", "Method"])  # Header row

def menu():

    menu = """Here’s our menu:\n1.Family size pizza - #8500\n2. Meat pie - #1000\n3. Smoothie - #1000\n4. Sharwama - #2500\n5. Bagels - #1500\n6. Ice cream - #2000
7. Chicken - #3000\n\nReply with the item number to order."""
    return menu


@app.route('/bot', methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').strip().lower()
    sender = request.values.get('From', '').replace("whatsapp:", "")
    response = MessagingResponse()
    msg = response.message()

    # Initialize conversation
    if sender not in customer_data:
        customer_data[sender] = {"state": "welcome"}
        msg.body("""Welcome to Your Cravings! We are here to serve you delicious meals. I am a chatbot here to make your order smooth and seamless.
        Choose the most suitable of the following options:.\n\nChoose an option:\n1. Place an order\n2. Contact an agent\n3. About us  \n\nType the corresponding number.""")
        return str(response)

    # Fetch the customer's current state
    state = customer_data[sender]["state"]

    # Handle different states
    if state == "welcome":
        if incoming_msg == "1":
            customer_data[sender]["state"] = "menu"
            msg.body(menu())
            # msg.body("""Here’s our menu:\n\n 1.  Fried Rice with chicken - #4500\n2. Jollof rice with beef - #3000\n3. Spaghetti - #2500\n4. Sharwama - #2500
            # \n5. Meat pie - #1000\n\nReply with the item number to order.""")
        elif incoming_msg == "2":
            msg.body("You can contact our agent at +08133814443. Let us know if you need anything else!")
        elif incoming_msg == "3":
            msg.body("We are Your Cravings, committed to serving the best meals. Established in 2020, we pride ourselves on fresh ingredients and quick service!")
        else:
            msg.body("Invalid option. Please choose:\n1. Place an order\n2. Contact an agent\n3. About us")

    elif state == "menu":
        if incoming_msg in ["1", "2", "3",'4','5']:
            item = {"1": "Family size pizza", "2": "Meat pie", "3": "Smoothie", "4": "Sharwama", "5": "Bagels", "6": "Ice cream", "7": "Chicken"}[incoming_msg]
            customer_data[sender]["order"] = {"item": item, "quantity": 0}
            customer_data[sender]["state"] = "quantity"
            msg.body(f"You selected {item}. How many would you like to order?")
        else:
            msg.body("Please reply with a valid item number (1, 2, or 3).")

    elif state == "quantity":
        if incoming_msg.isdigit():
            quantity = int(incoming_msg)
            customer_data[sender]["order"]["quantity"] = quantity
            customer_data[sender]["state"] = "delivery"
            msg.body(f"Order summary:\nItem: {customer_data[sender]['order']['item']}\nQuantity: {quantity}\n\nWould you like delivery or pick-up? Reply with 'd' for'delivery' or 'p' for 'pick-up'.")
        else:
            msg.body("Please enter a valid quantity.")

    elif state == "delivery":
        if incoming_msg in ["delivery", "pick-up",'d', 'p']:
            customer_data[sender]["order"]["method"] = incoming_msg
            customer_data[sender]["state"] = "confirmed"
            save_to_csv(sender, customer_data[sender])  # Save data to CSV
            if incoming_msg == 'p':
                incoming_msg = "pick-up"
            if incoming_msg == 'd':
                incoming_msg = "delivery"
            msg.body(f"Thank you! Your order for {customer_data[sender]['order']['quantity']} {customer_data[sender]['order']['item']} via {incoming_msg} has been placed. Reply 'menu' to start a new order or 'exit' to end.")
        else:
            msg.body("Please reply with 'delivery' or 'pick-up'.")

    elif state == "confirmed":
        if incoming_msg == "menu":
            customer_data[sender]["state"] = "menu"
            msg.body(menu())

        elif incoming_msg == "exit":
            del customer_data[sender]
            msg.body("Thank you for choosing Your Cravings. Have a great day!")
        else:
            msg.body("Reply 'menu' to start a new order or 'exit' to end.")

    return str(response)


def save_to_csv(sender, data):
    """
    Save customer data to a CSV file.
    """
    with open(CSV_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        # Extract relevant details
        row = [
            sender,
            data.get("state", ""),
            data["order"].get("item", ""),
            data["order"].get("quantity", ""),
            data["order"].get("method", ""),
        ]
        writer.writerow(row)



if __name__ == "__main__":
    app.run(port=5000)
