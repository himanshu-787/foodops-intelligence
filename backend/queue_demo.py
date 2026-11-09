import queue
import threading
import time

events = queue.Queue()
processed = set()          # idempotent consumer: kaunse order ho chuke


def place_order(order_id):
    # Zaroori kaam: turant ho gaya
    print(f"Order {order_id} saved")
    events.put({"event": "ORDER_PLACED", "order_id": order_id})   # baaki kaam baad mein
    print(f"Order {order_id}: customer ko turant response mil gaya")


def sms_worker():
    while True:
        msg = events.get()
        if msg is None:                       # band karne ka signal
            break
        oid = msg["order_id"]
        if oid in processed:                  # duplicate aaya toh dobara mat karo
            print(f"  SMS skip (duplicate) order {oid}")
        else:
            time.sleep(1)                     # SMS bhejne mein time lagta hai
            print(f"  SMS bheja order {oid}")
            processed.add(oid)
        events.task_done()


worker = threading.Thread(target=sms_worker)
worker.start()

place_order(1)
place_order(2)
events.put({"event": "ORDER_PLACED", "order_id": 2})   # duplicate delivery ka simulation

events.put(None)
worker.join()