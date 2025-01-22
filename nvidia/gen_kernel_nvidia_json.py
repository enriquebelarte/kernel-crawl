#!/usr/bin/env python3

import json
import subprocess
from datetime import datetime, timedelta

def filter_releases(releases_json, release_type, age_days):
    """
    Filters releases based on type and age.

    Args:
        releases_json: JSON data containing release information.
        release_type: Type of release to filter (e.g., "lts branch", "production branch").
        age_days: Maximum age of releases in days.

    Returns:
        List of filtered releases.
    """
    filtered_releases = []
    for release in releases_json:
        if release['type'] == release_type:
            for driver_info in release['driver_info']:
                release_date = datetime.strptime(driver_info['release_date'], '%Y-%m-%d')
                if (datetime.now() - release_date) <= timedelta(days=age_days):
                    filtered_releases.append(driver_info)
    return filtered_releases

def create_image_name(registry, driver_name, release_version, kernel_version):
    """
    Creates the image name.

    Args:
        registry: Container registry.
        driver_name: Name of the driver.
        release_version: Release version.
        kernel_version: Kernel version.

    Returns:
        Image name string.
    """
    return f"{registry}/{driver_name}:{release_version}-{kernel_version}"

def check_image_exists(image_name):
    """
    Checks if the image exists.

    Args:
        image_name: Name of the image.

    Returns:
        True if the image exists, False otherwise.
    """
    try:
        subprocess.run(["skopeo", "inspect", f"docker://{image_name}"], check=True, stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    data_dir = "data"
    registry = "quay.io/ebelarte"
    driver_name = "nvidia-build-drivers"
    lts_age_days = 3 * 365
    prod_age_days = 365

    with open(f"{data_dir}/filtered_releases.json", "r") as f:
        releases_json = json.load(f)

    with open(f"{data_dir}/kernel_versions.json", "r") as f:
        kernel_versions_json = json.load(f)
        kernel_versions = [tag for tag in kernel_versions_json['Tags'] if tag.startswith("5")]

    release_matrix = []
    for kernel_version in kernel_versions:
        lts_releases = filter_releases(releases_json, "lts branch", lts_age_days)
        prod_releases = filter_releases(releases_json, "production branch", prod_age_days)

        for release in lts_releases + prod_releases:
            image_name = create_image_name(registry, driver_name, release['release_version'], kernel_version)
            release['image'] = image_name
            release['published'] = check_image_exists(image_name)
            release_matrix.append(release)

    with open(f"{data_dir}/drivers_matrix.json", "w") as f:
        json.dump(release_matrix, f, indent=4)

    if all(release['published'] for release in release_matrix):
        print("No versions found at matrix to be built. All published yet.")
    else:
        print("New versions found at matrix. Running build pipeline.")

if __name__ == "__main__":
    main()
