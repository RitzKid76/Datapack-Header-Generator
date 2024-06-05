import sys
import docs
import new_lines

folder_path = sys.argv[1]

docs.process_files(folder_path)
new_lines.process_files(folder_path)
