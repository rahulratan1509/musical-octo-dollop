import subprocess

# List of packages to install

package_to_install = [
  "django",
  "openpyxl",
]

#install each package using pip
for package in package_to_install:
  subprocess.call(["pip", "install", package])
