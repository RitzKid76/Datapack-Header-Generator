import os

accepable_file_types = ("json", "mcfunction", "txt")

def remove_extra_newlines(file_path):
    with open(file_path, 'r+') as file:
        f = file.read()
        file.seek(0)
        file.truncate(0)
        
        file.write(''.join(f).rstrip('\n') + '\n')
        
def process_files(folder_path):
    items = os.listdir(folder_path)

    for item in items:
        item_path = os.path.join(folder_path, item)

        if os.path.isfile(item_path):
            if item_path.endswith(accepable_file_types):
                remove_extra_newlines(item_path)

        elif os.path.isdir(item_path):
            process_files(item_path)
