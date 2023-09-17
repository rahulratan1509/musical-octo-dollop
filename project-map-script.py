import os

def create_directory_structure_map(root_directory, output_file):
    with open(output_file, 'w') as file:
        for root, dirs, files in os.walk(root_directory):
            depth = root.count(os.sep) - root_directory.count(os.sep)
            indent = '    ' * depth
            file.write(f"{indent}{os.path.basename(root)}/\n")
            subindent = '    ' * (depth + 1)

            for file_name in files:
                file.write(f"{subindent}{file_name}\n")

if __name__ == "__main__":
    project_root = r'C:\Users\Retro\Desktop\Django Project\musical-octo-dollop'  # Replace with your project directory path
    output_map_file = 'project_directory_map.txt'  # Output file for the directory structure map

    create_directory_structure_map(project_root, output_map_file)
    print(f"Directory structure map saved to {output_map_file}")
