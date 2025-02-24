import os

accepable_file_types = ("json", "mcfunction", "txt")

def clean_line(line):
    return line.rstrip() + "\n"


def remove_extra_newlines(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    with open(file_path, 'w') as f:
        for line in lines:
            f.write(clean_line(line))

def process_files(folder_path):
    items = os.listdir(folder_path)

    for item in items:
        item_path = os.path.join(folder_path, item)

        if os.path.isfile(item_path):
            if item_path.endswith(accepable_file_types):
                remove_extra_newlines(item_path)

        elif os.path.isdir(item_path):
            process_files(item_path)
