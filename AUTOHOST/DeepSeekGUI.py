import json
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load IPBank.json
def load_ip_bank(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to update the right panel when an IP is selected
def on_ip_select(event):
    selected_ip = ip_listbox.get(ip_listbox.curselection())
    ip_data = ip_bank[selected_ip]

    # Clear previous data
    resolved_domain_label.config(text="")
    services_label.config(text="Services:\n")
    endpoints_label.config(text="Endpoints:\n")
    ax.clear()

    # Update Resolved Domain
    resolved_domain = ip_data['ResolvedDomain'] if ip_data['ResolvedBoolean'] else selected_ip
    resolved_domain_label.config(text=f"Resolved Domain: {resolved_domain}")

    # Plot ports
    ports = set(ip_data.get('Ports', []))
    potential_ports = set(ip_data.get('PotentialPorts', []))
    all_ports = ports.union(potential_ports)

    # Plot circles
    for i, port in enumerate(all_ports):
        color = 'green' if port in ports else 'orange'
        circle = plt.Circle((i * 2, 0), 0.5, color=color)
        ax.add_patch(circle)
        ax.text(i * 2, 0, str(port), ha='center', va='center', color='white')

    ax.set_xlim(-1, len(all_ports) * 2)
    ax.set_ylim(-1, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    canvas.draw()

    # Update Services
    services = ip_data.get('Services', [])
    services_label.config(text="Services:\n" + "\n".join(services))

    # Update Endpoints
    endpoints = ip_data.get('Endpoints', [])
    endpoints_label.config(text="Endpoints:\n" + "\n".join(endpoints))

# Load IPBank.json
ip_bank = load_ip_bank('IPBank.json')

# Create GUI
root = tk.Tk()
root.title("IP Bank Viewer")

# Left Panel: IP List
left_panel = tk.Frame(root, width=200, height=400)
left_panel.pack(side=tk.LEFT, fill=tk.Y)

ip_listbox = tk.Listbox(left_panel)
ip_listbox.pack(fill=tk.BOTH, expand=True)

for ip in ip_bank.keys():
    ip_listbox.insert(tk.END, ip)

ip_listbox.bind('<<ListboxSelect>>', on_ip_select)

# Right Panel: IP Details
right_panel = tk.Frame(root, width=600, height=400)
right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Resolved Domain
resolved_domain_label = tk.Label(right_panel, text="", font=('Arial', 14))
resolved_domain_label.pack(pady=10)

# Matplotlib Figure for Ports
fig, ax = plt.subplots(figsize=(6, 2))
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.axis('off')
canvas = FigureCanvasTkAgg(fig, master=right_panel)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Services
services_label = tk.Label(right_panel, text="Services:\n", font=('Arial', 12), justify=tk.LEFT)
services_label.pack(pady=10)

# Endpoints
endpoints_label = tk.Label(right_panel, text="Endpoints:\n", font=('Arial', 12), justify=tk.LEFT)
endpoints_label.pack(pady=10)

# Run the GUI
root.mainloop()
