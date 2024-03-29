import os

template_file = "docker-compose.template.yaml"
output_file = "docker-compose.yaml"

with open(template_file, "r") as f:
    template = f.read()

zoom_path = input("Enter the absolute path to the Zoom data directory (unquoted): ")

# Replace the placeholders with the values that you want to use.
template = template.replace("{{ zoom_path }}", zoom_path)

# Write the generated Docker Compose file to disk.
with open(output_file, "w") as f:
    f.write(template)
