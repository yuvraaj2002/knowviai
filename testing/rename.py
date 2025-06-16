root_folder = "knowledge_base/class_12/vistas"
import os

new_names = [
    "The Third Level",
    "The Tiger King", 
    "Journey to the end of the Earth",
    "The Enemy",
    "On the Face of It",
    "Memories of Childhood"
]

files = [f for f in os.listdir(root_folder) if f.endswith(".pdf")]
files.sort()  # Sort to ensure consistent order

for old_name, new_name in zip(files, new_names):
    old_path = os.path.join(root_folder, old_name)
    new_path = os.path.join(root_folder, new_name + ".pdf")
    os.rename(old_path, new_path)