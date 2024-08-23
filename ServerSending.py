import tkinter as tk
from tkinter import messagebox
import requests

# Function to send job data to the Flask server
def send_job(job_id, tank_times, tank_nums, speed):
    job_data = [job_id, tank_times, tank_nums]
    try:
        response = requests.post('http://192.168.15.145:5000/add_job_list', json=job_data)
        response.raise_for_status()
        messagebox.showinfo("Success", f"Job {job_id} sent successfully")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to send job: {e}")

# Create the main application window
root = tk.Tk()
root.title("Device Controller")
root.geometry("400x400")

# Job ID Entry
tk.Label(root, text="Job ID").pack(pady=5)
job_id_entry = tk.Entry(root)
job_id_entry.pack(pady=5)

# Tank Times Entry
tk.Label(root, text="Tank Times (comma-separated)").pack(pady=5)
tank_times_entry = tk.Entry(root)
tank_times_entry.pack(pady=5)

# Tank Numbers Entry
tk.Label(root, text="Hoist Speed").pack(pady=5)
hoist_speed_entry = tk.Entry(root)
hoist_speed_entry.pack(pady=5)

# speed Entry
tk.Label(root, text="Tank Numbers (comma-separated)").pack(pady=5)
tank_nums_entry = tk.Entry(root)
tank_nums_entry.pack(pady=5)

# Dropdown for Number of Zones
tk.Label(root, text="Number of Zones").pack(pady=5)
zone_count_var = tk.StringVar(root)
zone_count_var.set("1")  # Default value
zone_count_menu = tk.OptionMenu(root, zone_count_var, *range(1, 10))
zone_count_menu.pack(pady=5)

# Send Job Button
def send_job_button_click():
    job_id = int(job_id_entry.get())

    speed = int(hoist_speed_entry.get())
    
    # Parse tank times and insert "START" and "END"
    tank_times = list(map(int, tank_times_entry.get().split(',')))
    tank_times.insert(0, "START")
    tank_times.append("END")
    
    # Parse tank numbers and insert initial tank (0) and last zone
    tank_nums = list(map(int, tank_nums_entry.get().split(',')))
    tank_nums.insert(0, 0)  # Add initial tank 0
    
    # Calculate the last zone based on the number of zones selected
    num_zones = int(zone_count_var.get())
    tank_nums.append(num_zones - 1)  # Add last zone number

    send_job(job_id, tank_times, tank_nums, speed)

send_button = tk.Button(root, text="Send Job", command=send_job_button_click)
send_button.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()
