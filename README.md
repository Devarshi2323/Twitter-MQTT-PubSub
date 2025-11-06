# Twitter-like MQTT Publisher–Subscriber

A Python application that simulates Twitter-style messaging using the MQTT publish/subscribe model.

## Features
- Publisher GUI: send messages (tweets) under any hashtag
- Subscriber GUI: subscribe/unsubscribe to hashtags in real time
- Real-time message delivery via MQTT broker
- Multiple subscribers can receive the same tweet simultaneously

## Technologies
- **Python 3**
- **Tkinter** – GUI framework
- **Paho-MQTT** – MQTT client library
- Broker: [test.mosquitto.org](https://test.mosquitto.org) (port 1883)

## Setup
1. Create and activate a virtual environment  
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   # or
   source .venv/bin/activate   # macOS/Linux
   ```
2. Install the dependency  
   ```bash
   pip install paho-mqtt
   ```
3. Run both applications  
   ```bash
   python subscriber.py
   python publisher.py
   ```

## Usage
1. In both GUIs, connect to the same broker (`test.mosquitto.org`, 1883).  
2. In the subscriber, enter a hashtag (e.g. `#Tech`) and click **Subscribe**.  
3. In the publisher, enter username, tweet, and the same hashtag, then click **Publish Tweet**.  
4. The subscriber feed displays the message in real time.

## Example Output
```
[hashtags/News] Darsh: This is breaking news
[hashtags/News] Darsh: ohh wow
```

## Author
Devarshi Patel / Darsh Gondaliya 
