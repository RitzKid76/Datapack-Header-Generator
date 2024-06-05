import os
import re
import json

log = ""

function_map = {}
macros = []

def clear_headers(dir):
    with open(dir, "r") as f:
        lines = f.readlines()
        output = ""
        try:
            while(lines[0].startswith(("#>", "\n"))):
                lines.pop(0)
            for line in lines:
                output += line
        except IndexError as e:
            add_to_log(f"EMPTY FILE: {dir}\n")

    with open(dir, "w") as f:
        f.write(output)

def dir_to_server_call(dir):
    dir = dir.split(root + "\\data\\")[1].split("\\tags\\functions\\")

    namespace = dir[0]
    advanement = dir[1].replace("\\", "/").split(".")[0]

    return f"server {namespace}:{advanement}"

def dir_to_advancement(dir):
    dir = dir.split(root + "\\data\\")[1].split("\\advancements\\")

    namespace = dir[0]
    advanement = dir[1].replace("\\", "/").split(".")[0]

    return f"advancement {namespace}:{advanement}"

def dir_to_mcfunction(dir):
    dir = dir.split(root + "\\data\\")[1].split("\\functions\\")
    
    namespace = dir[0]
    function = dir[1].replace("\\", "/").split(".")[0]

    return f"{namespace}:{function}"

def get_macro(caller, function):
    pattern = r"\$\(.*?\)"    
    matches = re.findall(pattern, function)
    if matches:
        macros.append([caller, function])
        add_caller(caller, function)

def match_macro(function):
    for macro in macros:
        c = macro[0]
        f = macro[1]
        pattern = re.sub(r'\$\(.*?\)', r'([^/]+)', f)
        
        match = re.match(pattern, function)

        if match and function != c:
            return macro
            
    return ""

def function_distance(a, b):
    a = re.split(r"[\/:]", a)
    b = re.split(r"[\/:]", b)

    if len(a) > len(b):
        return 2

    while(
        len(a) and
        len(b) and
        a[0] == b[0]
    ):
        a.pop(0)
        b.pop(0)
    
    return len(a) + len(b) - 2

def relative_call(caller, function):
    distance = function_distance(caller, function)
    split = re.split(r"[\/:]", caller)
    local = split[-1]
    caller_namespace = split[0]
    function_namespace = function.split(":")[0]
    output = ""

    if distance < 2:
        output += f"./{local}"
        if distance == 1:
            output = "." + output
    else:
        output = caller[:]
    
    namespace = caller_namespace
    split = caller_namespace.split()
    if(len(split) > 1):
        namespace = split[1]

    if(namespace == function_namespace):
        output = output.replace(namespace, ".", 1)
    return output

def add_caller(caller, function):
    if function not in function_map:
        function_map[function] = [caller]
    elif caller not in function_map[function]:
        function_map[function].insert(0, caller)

def get_caller(caller, function):
    macro = match_macro(caller)
    if(macro != ""):
        add_caller(function_map[macro[1]][0] + " ?", caller)
    if(function != ""):
        add_caller(caller, function)

def on_functions(dir, function):
    pattern = r"function [a-z]+:[a-z0-9_/$()]+"

    with open(dir, "r") as f:
        lines = f.readlines()

        for line in lines:
            matches = re.findall(pattern, line)
            
            if matches:
                called_from = dir_to_mcfunction(dir)
                mcfunction = matches[0].split(" ")[1]

                function(called_from, mcfunction)

def get_docs(function):
    if function in function_map:
        output = ""
        called_from = function_map[function]
        calls_self = False

        for call in called_from:
            if call == function:
                calls_self = True
            else:
                output += "#> " + relative_call(call, function) + "\n"
        if calls_self:
            output += "#> self\n"

        return output + "\n"
    else:
        add_to_log(f"POTENTIAL UNUSED FUNCTION: {function}\n")
        return "#> unknown\n\n"

def insert_docs(dir):
    with open(dir, "r") as f:
        contents = f.read()
    contents = get_docs(dir_to_mcfunction(dir)) + contents
    with open(dir, "w") as f:
        f.write(contents)

def run_on_tree(folder_path, function, accepable_file_types):
    items = os.listdir(folder_path)

    for item in items:
        item_path = os.path.join(folder_path, item)

        if os.path.isfile(item_path):
            if item_path.endswith(accepable_file_types):
                function(item_path)

        elif os.path.isdir(item_path):
            run_on_tree(item_path, function, accepable_file_types)

def get_all_macros(dir):
    on_functions(dir, get_macro)

def get_all_callers(dir):
    pattern = r"function [a-z]+:[a-z0-9_/$()]+"

    with open(dir, "r") as f:
        lines = f.readlines()

        for line in lines:
            matches = re.findall(pattern, line)
            
            called_from = dir_to_mcfunction(dir)
            if matches:
                for match in matches:
                    mcfunction = match.split(" ")[1]
                    get_caller(called_from, mcfunction)
            else:
                get_caller(called_from, "")

def is_advancement(json_data):
    return "rewards" in json_data

def get_advancement_callers(dir):
    with open(dir, "r") as f:
        data = json.load(f)
        if is_advancement(data):
            rewards = data["rewards"]
            if "function" in rewards:
                function = rewards["function"]
                advancement = dir_to_advancement(dir)
                add_caller(advancement, function)

def write_to_log():
    script_folder = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_folder, "log.txt"), "w") as f:
        f.write(log)

def add_to_log(string):
    global log
    log += string

def is_server(dir):
    return "data\\minecraft\\tags\\functions\\" in dir

def get_server_callers(dir):
    if is_server(dir):
        with open(dir, "r") as f:
            data = json.load(f)
            values = data["values"]
            for value in values:
                add_caller(dir_to_server_call(dir), value)

def process_files(folder_path):
    global root
    root = folder_path

    run_on_tree(folder_path, get_server_callers, ("json"))
    run_on_tree(folder_path, get_advancement_callers, ("json"))

    run_on_tree(folder_path, clear_headers, ("mcfunction"))
    run_on_tree(folder_path, get_all_macros, ("mcfunction"))
    run_on_tree(folder_path, get_all_callers, ("mcfunction"))
    run_on_tree(folder_path, insert_docs, ("mcfunction"))
    
    write_to_log()