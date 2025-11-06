# Technical Report – Twitter-like MQTT Publisher–Subscriber

## 1. Introduction
This project implements a **Twitter-like real-time communication system** using the **Publish–Subscribe model** over MQTT.  
Users can publish short text messages (“tweets”) under hashtags, and subscribers instantly receive those tweets in real time through an MQTT broker.

Two Python GUI programs were developed:
- **Publisher.py** – posts tweets to specific hashtags  
- **Subscriber.py** – subscribes/unsubscribes to hashtags and displays incoming tweets

---

## 2. System Architecture
```
        +--------------------+
        |   Publisher GUI    |
        |  (paho-mqtt/tkinter) 
        +---------+----------+
                  |
                  | MQTT Publish (topic = hashtags/<tag>)
                  v
        +--------------------+
        |   MQTT Broker      |
        |  (test.mosquitto.org)
        +---------+----------+
                  ^
                  | MQTT Subscribe (topic = hashtags/<tag>)
        +---------+----------+
        |   Subscriber GUI   |
        |  (paho-mqtt/tkinter)
        +--------------------+
```

**Workflow:**
1. The Publisher connects to the MQTT broker and publishes messages to a topic that represents a hashtag.  
2. The Subscriber connects to the same broker and subscribes to that topic.  
3. The broker distributes the published message to all active subscribers in real time.

---

## 3. Client Communication
- Communication uses the **MQTT protocol** (Message Queuing Telemetry Transport), which is lightweight and ideal for real-time updates.
- Each message includes a **topic** (`hashtags/<tag>`) and a **payload** (`<username>: <tweet>`).
- The broker handles all message delivery — publishers and subscribers never communicate directly.
- Multiple subscribers can listen to the same topic and receive identical messages simultaneously, demonstrating one-to-many broadcasting.

---

## 4. Threading and Real-Time Behavior
Both applications use:
```python
client.loop_start()
```
This starts a **background network thread** that handles incoming and outgoing MQTT traffic without freezing the GUI.  
Tkinter runs on the main thread, while MQTT callbacks (like `on_message`) run asynchronously, ensuring smooth and responsive UIs even during continuous message flow.

---

## 5. Clock Synchronization Concept
Although MQTT itself doesn’t provide clock sync, timestamps or ordering can be handled by the broker or embedded in messages if needed.  
In this project, messages are effectively “synchronized” through the broker’s queueing system — all clients receive updates almost instantly, providing near-real-time coordination.

---

## 6. Testing and Results
- **Broker:** `test.mosquitto.org` (public, port 1883)  
- **Tested Scenarios:**  
  - Single Publisher, multiple Subscribers (#News, #Tech, #Data)  
  - Simultaneous subscriptions to multiple hashtags  
  - Publish/Unsubscribe/Disconnect operations  
- **Result:** All messages were delivered instantly and correctly to relevant subscribers with stable connections.

---

## 7. Conclusion
The implemented system fulfills all assignment requirements by demonstrating a complete **Publisher–Subscriber communication model** using MQTT with real-time updates and a user-friendly Tkinter GUI.  
It successfully shows how event-driven communication enables efficient broadcast of messages across multiple clients in real time.

---

**Developed by:**  
Devarshi Patel 
Darsh Gondaliya  
Course: COSC 4437 – Distributed Systems  

