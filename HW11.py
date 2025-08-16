from datetime import datetime, timedelta
import queue
import threading
import time
import random

OrderRequestBody = tuple[str, datetime]

storage = {
    "users": [],
    "dishes": [
        {"id": 1, "name": "Salad", "value": 1099, "restaurant": "Silpo"},
        {"id": 2, "name": "Soda", "value": 199, "restaurant": "Silpo"},
        {"id": 3, "name": "Pizza", "value": 599, "restaurant": "Kvadrat"},
    ],
    # ...
}


class Scheduler:
    def __init__(self, delivery_queue: queue.Queue[OrderRequestBody]):
        self.orders: queue.Queue[OrderRequestBody] = queue.Queue()
        self.delivery_queue = delivery_queue

    def process_orders(self) -> None:
        print("SCHEDULER PROCESSING...")

        while True:
            order = self.orders.get(True)
            time_to_wait = order[1] - datetime.now()

            if time_to_wait.total_seconds() > 0:
                # Not ready yet, put it back and wait a little
                self.orders.put(order)
                time.sleep(0.5)
            else:
                print(f"\n\t{order[0]} READY, SENDING TO DELIVERY QUEUE")
                self.delivery_queue.put(order)

    def add_order(self, order: OrderRequestBody) -> None:
        self.orders.put(order)
        print(f"\n\t{order[0]} ADDED FOR PROCESSING")


class DeliveryHandler:
    def __init__(self):
        self.providers = ["uklon", "uber"]
        self.deliveries: queue.Queue[OrderRequestBody] = queue.Queue()

    def process_deliveries(self) -> None:
        print("DELIVERY PROCESSING...")

        while True:
            order = self.deliveries.get(True)
            provider = random.choice(self.providers)

            print(f"\n\t{order[0]} PICKED UP BY {provider.upper()}")

            if provider == "uklon":
                time.sleep(5)
            else:  # uber
                time.sleep(3)

            print(f"\n\t{order[0]} DELIVERED BY {provider.upper()}")


def main():
    delivery_handler = DeliveryHandler()
    scheduler = Scheduler(delivery_handler.deliveries)

    # Start scheduler thread
    scheduler_thread = threading.Thread(target=scheduler.process_orders, daemon=True)
    scheduler_thread.start()

    # Start delivery handler thread
    delivery_thread = threading.Thread(target=delivery_handler.process_deliveries, daemon=True)
    delivery_thread.start()

    # User input loop
    while True:
        order_details = input("Enter order details (e.g. A 5): ")
        data = order_details.split(" ")

        order_name = data[0]
        delay = datetime.now() + timedelta(seconds=int(data[1]))

        scheduler.add_order(order=(order_name, delay))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        raise SystemExit(0)