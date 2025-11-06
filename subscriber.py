import tkinter as tk
from tkinter import messagebox
import re
import paho.mqtt.client as mqtt

DEFAULT_BROKER = "test.mosquitto.org"
DEFAULT_PORT = 1883
TOPIC_PREFIX = "hashtags/"

def normalize_hashtag(raw: str) -> str:
    tag = raw.strip()
    if tag.startswith("#"):
        tag = tag[1:]
    tag = re.sub(r"[^\w]", "_", tag)
    return tag

class SubscriberApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitter-like Subscriber (MQTT)")
        self.client = None
        self.connected = False
        self.subscriptions = set()

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

        # Hashtag controls
        tk.Label(frm, text="Hashtag:").grid(row=1, column=0, sticky="e")
        self.hashtag_entry = tk.Entry(frm, width=20)
        self.hashtag_entry.grid(row=1, column=1, sticky="w", pady=2)

        self.connect_btn = tk.Button(frm, text="Connect", command=self.connect_broker)
        self.connect_btn.grid(row=2, column=0, pady=8, sticky="we")

        self.sub_btn = tk.Button(frm, text="Subscribe", command=self.subscribe_hashtag, state="disabled")
        self.sub_btn.grid(row=2, column=1, pady=8, sticky="we")

        self.unsub_btn = tk.Button(frm, text="Unsubscribe", command=self.unsubscribe_hashtag, state="disabled")
        self.unsub_btn.grid(row=2, column=2, pady=8, sticky="we")

        self.disconnect_btn = tk.Button(frm, text="Disconnect", command=self.disconnect_broker, state="disabled")
        self.disconnect_btn.grid(row=2, column=3, pady=8, sticky="we")

        # Subscribed list
        tk.Label(frm, text="Subscribed hashtags:").grid(row=3, column=0, columnspan=4, sticky="w", pady=(6,0))
        self.tags_list = tk.Listbox(frm, height=4)
        self.tags_list.grid(row=4, column=0, columnspan=4, sticky="nsew")

        # Messages
        tk.Label(frm, text="Tweet feed:").grid(row=5, column=0, columnspan=4, sticky="w", pady=(8,0))
        self.feed = tk.Text(frm, height=12, state="disabled")
        self.feed.grid(row=6, column=0, columnspan=4, sticky="nsew")

        # Status
        self.status_var = tk.StringVar(value="Disconnected")
        self.status_lbl = tk.Label(frm, textvariable=self.status_var, fg="gray")
        self.status_lbl.grid(row=7, column=0, columnspan=4, sticky="w", pady=(6,0))

        # Resizing
        for c in range(4):
            frm.grid_columnconfigure(c, weight=1)
        frm.grid_rowconfigure(6, weight=1)

    # ---- MQTT callbacks ----
    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            self.status_var.set("Connected to broker")
            self.sub_btn.config(state="normal")
            self.unsub_btn.config(state="normal")
            self.disconnect_btn.config(state="normal")
            self.connect_btn.config(state="disabled")
        else:
            self.status_var.set(f"Connect failed (rc={rc})")

    def on_disconnect(self, client, userdata, rc, properties=None):
        self.connected = False
        self.status_var.set("Disconnected")
        self.sub_btn.config(state="disabled")
        self.unsub_btn.config(state="disabled")
        self.disconnect_btn.config(state="disabled")
        self.connect_btn.config(state="normal")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        text = msg.payload.decode("utf-8", errors="replace")
        self.append_feed(f"[{topic}] {text}")

    # ---- Helpers ----
    def append_feed(self, line: str):
        self.feed.config(state="normal")
        self.feed.insert("end", line + "\n")
        self.feed.see("end")
        self.feed.config(state="disabled")

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
        self.client.on_message = self.on_message

        try:
            self.client.connect(host, port, keepalive=60)
        except Exception as e:
            messagebox.showerror("MQTT", f"Failed to connect: {e}")
            return

        self.client.loop_start()
        self.status_var.set("Connecting...")

    def subscribe_hashtag(self):
        if not self.connected:
            messagebox.showwarning("Not connected", "Connect first.")
            return
        tag = normalize_hashtag(self.hashtag_entry.get())
        if not tag:
            messagebox.showwarning("Missing hashtag", "Enter a hashtag to subscribe.")
            return
        topic = f"{TOPIC_PREFIX}{tag}"
        try:
            self.client.subscribe(topic, qos=0)
            if topic not in self.subscriptions:
                self.subscriptions.add(topic)
                self.tags_list.insert("end", topic)
            self.status_var.set(f"Subscribed to '{topic}'")
        except Exception as e:
            messagebox.showerror("Subscribe error", str(e))

    def unsubscribe_hashtag(self):
        if not self.connected:
            messagebox.showwarning("Not connected", "Connect first.")
            return
        selection = self.tags_list.curselection()
        if not selection:
            messagebox.showinfo("Select a topic", "Pick one from the list to unsubscribe.")
            return

        idx = selection[0]
        topic = self.tags_list.get(idx)
        try:
            self.client.unsubscribe(topic)
            self.subscriptions.discard(topic)
            self.tags_list.delete(idx)
            self.status_var.set(f"Unsubscribed from '{topic}'")
        except Exception as e:
            messagebox.showerror("Unsubscribe error", str(e))

    def disconnect_broker(self):
        if self.client:
            try:
                self.client.disconnect()
                self.client.loop_stop()
            except Exception:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = SubscriberApp(root)
    root.mainloop()
