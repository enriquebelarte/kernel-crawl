import json
import requests
import os
import time

# Function to load and save remote JSONs for kernels and drivers
def download_json(url, local_path):
    response = requests.get(url)
    response.raise_for_status() 
    return response.json()
    with open(local_path, "w") as file:
        json.dump(json_data, file, indent=4)
    print(f"Downloaded JSON from {url} and saved to {local_path}")
    return json_data

# Load config parameters
def load_config(config_file):
    with open(config_file, "r") as file:
        return json.load(file)

config_file = "config.json"
config = load_config(config_file)
kernel_url = config["kernel_url"]
driver_url = config["driver_url"]
# Directory where original (source of truth) JSONs will be downloaded to
source_dir = config["source_dir"]
data_dir = config["data_dir"]

# Fetch and save kernel.json and driver.json from URLs
#kernel_json = load_json_from_url(kernel_url)
#driver_json = load_json_from_url(driver_url)
# Save them
os.makedirs(source_dir, exist_ok=True)  
kernel_local_path = os.path.join(source_dir, "kernel.json")
driver_local_path = os.path.join(source_dir, "driver.json")
kernel_json = download_json(kernel_url, kernel_local_path)
driver_json = download_json(driver_url, driver_local_path)

# Generate the kernel/driver matrix JSON
output_json = {"KERNEL_VERSION": {}}
for kernel_version, kernel_list in kernel_json["kernel-versions"].items():
    for kernel in kernel_list:
        # Add the kernel version if not already present
        if kernel not in output_json["KERNEL_VERSION"]:
            output_json["KERNEL_VERSION"][kernel] = {"DRIVER_VERSION": {}}
        
        # Copy driver versions for each kernel
        for driver_version, driver_data in driver_json["DRIVER_VERSION"].items():
            output_json["KERNEL_VERSION"][kernel]["DRIVER_VERSION"][driver_version] = driver_data

# Save matrix to a file
ts = int(time.time())
output_filename = data_dir+f"matrix-{ts}.json"
with open(output_filename, "w") as outfile:
    json.dump(output_json, outfile, indent=4)

print(f"Combined JSON saved to {output_filename}")

