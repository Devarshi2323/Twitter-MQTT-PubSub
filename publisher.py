import tkinter as tk
from tkinter import messagebox
import re
import threading
import paho.mqtt.client as mqtt

# ---------- Config defaults ----------
DEFAULT_BROKER = "test.mosquitto.org"
DEFAULT_PORT = 1883
TOPIC_PREFIX = "hashtags/"  # final topic will be hashtags/<TAG>

def normalize_hashtag(raw: str) -> str:
    """Turn '#AI ' or ' ai' into 'AI' and ensure it's alnum/underscore."""
    tag = raw.strip()
    if tag.startswith("#"):
        tag = tag[1:]
    # Allow letters, numbers, underscore only for MQTT topic safety
    tag = re.sub(r"[^\w]", "_", tag)
    return tag

class PublisherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitter-like Publisher (MQTT)")
        self.client = None
        self.connected = False

        # ---- UI ----
        frm = tk.Frame(root, padx=12, pady=12)
        frm.pack(fill="both", expand=True)

        # Broker settings
        tk.Label(frm, text="Broker host:").grid(row=0, column=0, sticky="e")
        self.broker_entry = tk.Entry(frm, width=30)
        self.broker_entry.insert(0, DEFAULT_BROKER)
        self.broker_entry.grid(row=0, column=1, sticky="w", pady=2)

        tk.Label(frm, text="Port:").grid(row=0, column=2, sticky="e")
        self.port_entry = tk.Entry(frm, width=6)
        self.port_entry.insert(0, str(DEFAULT_PORT))
        self.port_entry.grid(row=0, column=3, sticky="w", pady=2)

        # Username
        tk.Label(frm, text="Username:").grid(row=1, column=0, sticky="e")
        self.username_entry = tk.Entry(frm, width=30)
        self.username_entry.grid(row=1, column=1, columnspan=3, sticky="we", pady=2)

        # Tweet
        tk.Label(frm, text="Tweet message:").grid(row=2, column=0, sticky="e")
        self.tweet_entry = tk.Entry(frm, width=50)
        self.tweet_entry.grid(row=2, column=1, columnspan=3, sticky="we", pady=2)

        # Hashtag
        tk.Label(frm, text="Hashtag:").grid(row=3, column=0, sticky="e")
        self.hashtag_entry = tk.Entry(frm, width=30)
        self.hashtag_entry.grid(row=3, column=1, sticky="w", pady=2)

        # Buttons
        self.connect_btn = tk.Button(frm, text="Connect", command=self.connect_broker)
        self.connect_btn.grid(row=4, column=0, pady=8, sticky="we")

        self.publish_btn = tk.Button(frm, text="Publish Tweet", command=self.publish_tweet, state="disabled")
        self.publish_btn.grid(row=4, column=1, columnspan=2, pady=8, sticky="we")

        self.disconnect_btn = tk.Button(frm, text="Disconnect", command=self.disconnect_broker, state="disabled")
        self.disconnect_btn.grid(row=4, column=3, pady=8, sticky="we")

        # Status
        self.status_var = tk.StringVar(value="Disconnected")
        self.status_lbl = tk.Label(frm, textvariable=self.status_var, fg="gray")
        self.status_lbl.grid(row=5, column=0, columnspan=4, sticky="w")

        # Make columns stretch
        for c in range(4):
            frm.grid_columnconfigure(c, weight=1)

    # ---- MQTT callbacks ----
    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            self.status_var.set("Connected to broker")
            self.publish_btn.config(state="normal")
            self.disconnect_btn.config(state="normal")
            self.connect_btn.config(state="disabled")
        else:
            self.status_var.set(f"Connect failed (rc={rc})")

    def on_disconnect(self, client, userdata, rc, properties=None):
        self.connected = False
        self.status_var.set("Disconnected")
        self.publish_btn.config(state="disabled")
        self.disconnect_btn.config(state="disabled")
        self.connect_btn.config(state="normal")

    # ---- Actions ----
    def connect_broker(self):
        host = self.broker_entry.get().strip()
        try:
            port = int(self.port_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Port must be a number.")
            return

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

        try:
            self.client.connect(host, port, keepalive=60)
        except Exception as e:
            messagebox.showerror("MQTT", f"Failed to connect: {e}")
            return

        # Non-blocking network loop
        self.client.loop_start()
        self.status_var.set("Connecting...")

    def publish_tweet(self):
        if not self.connected or not self.client:
            messagebox.showwarning("Not connected", "Connect to the broker first.")
            return

        username = self.username_entry.get().strip()
        msg = self.tweet_entry.get().strip()
        tag = normalize_hashtag(self.hashtag_entry.get())

        if not username or not msg or not tag:
            messagebox.showwarning("Missing data", "Username, Tweet, and Hashtag are required.")
            return

        topic = f"{TOPIC_PREFIX}{tag}"
        payload = f"{username}: {msg}"

        try:
            self.client.publish(topic, payload, qos=0, retain=False)
            self.status_var.set(f"Published to '{topic}'")
            # Optional: clear message box after publish
            self.tweet_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Publish error", str(e))

    def disconnect_broker(self):
        if self.client:
            try:
                self.client.disconnect()
                self.client.loop_stop()
            except Exception:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = PublisherApp(root)
    root.mainloop()
