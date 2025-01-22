import json
import requests

# Function to load remote JSONs for kernels and drivers
def load_json_from_url(url):
    response = requests.get(url)
    response.raise_for_status() 
    return response.json()

# Load config
def load_config(config_file):
    with open(config_file, "r") as file:
        return json.load(file)
config_file = "conf/config.json"
config = load_config(config_file)
kernel_url = config["kernel_url"]
driver_url = config["driver_url"]

# Fetch kernel.json and driver.json from URLs
kernel_json = load_json_from_url(kernel_url)
driver_json = load_json_from_url(driver_url)

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
output_filename = "combined_kernel_driver.json"
with open(output_filename, "w") as outfile:
    json.dump(output_json, outfile, indent=4)

print(f"Combined JSON saved to {output_filename}")

