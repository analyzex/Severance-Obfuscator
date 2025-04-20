import re
import random
import string
import os
import sys

def generate_text(length=10):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def create_var_name():
    return generate_text()

def create_var_value():
    return generate_text(random.randint(5, 15))

def create_junk_comment():
    return f":: {generate_text(random.randint(10, 30))} set %{generate_text()}% set set %{generate_text()}% set %{generate_text()}% set %{generate_text()}{generate_text()}% set set %{generate_text()}%"

def create_char_mappings():
    char_maps = []
    for _ in range(random.randint(10, 15)):
        current_mapping = {}
        for letter in string.ascii_lowercase:
            current_mapping[letter] = create_var_name()
        char_maps.append(current_mapping)
    return char_maps

def obscure_label(line_text, mappings):
    if re.match(r"^\s*:[a-zA-Z0-9_]+", line_text):
        label = line_text.split(":")[1].strip()
        hidden_label = generate_text(20)
        return f":{hidden_label}"
    return line_text

def obscure_goto(line_text, label_dict, mappings):
    if re.match(r"^\s*goto\s+[a-zA-Z0-9_]+", line_text, re.IGNORECASE):
        label = line_text.split("goto")[1].strip()
        hidden_label = label_dict.get(label, label)
        obscured_goto = []
        for char in "goto":
            if char.lower() in mappings[0]:
                var_set = random.choice(mappings)
                obscured_goto.append(f"%{var_set[char.lower()]}%")
            else:
                obscured_goto.append(char)
        obscured_goto = "".join(obscured_goto)
        return f"{obscured_goto} {hidden_label}"
    return line_text

def replace_chars_with_vars(script_text, mappings):
    processed_lines = []
    for original_line in script_text.splitlines():
        if re.match(r"^\s*:[a-zA-Z0-9_]+", original_line):
            processed_lines.append(original_line)
            continue

        if re.match(r"^\s*goto\s+[a-zA-Z0-9_]+", original_line, re.IGNORECASE):
            processed_lines.append(original_line)
            continue

        parts = re.split(r"(%[^%]+%)", original_line)
        new_line = []
        for part in parts:
            if re.match(r"%[^%]+%", part):
                new_line.append(part)
            else:
                transformed_part = []
                for character in part:
                    if character.lower() in mappings[0]:
                        var_set = random.choice(mappings)
                        transformed_part.append(f"%{var_set[character.lower()]}%")
                    else:
                        transformed_part.append(character)
                new_line.append("".join(transformed_part))
        processed_lines.append("".join(new_line))
    return "\n".join(processed_lines)

def split_into_blocks(script_text, block_size=1):
    lines = script_text.splitlines()
    return [lines[i:i + block_size] for i in range(0, len(lines), block_size)]

def add_fake_jumps(code_blocks):
    processed_blocks = []
    fake_markers = [generate_text(10) for _ in range(len(code_blocks))]

    for index, block in enumerate(code_blocks):
        marker = f":{fake_markers[index]}"
        processed_blocks.append(marker)
        processed_blocks.extend(block)

        if index < len(code_blocks) - 1:
            processed_blocks.append(f"goto {fake_markers[index + 1]}")
        else:
            processed_blocks.append("goto :eof")

    return "\n".join(processed_blocks)

def obfuscate_script(script_content):
    echo_directive = r"@echo\s+off"
    echo_match = re.search(echo_directive, script_content, re.IGNORECASE)
    if echo_match:
        echo_line = echo_match.group(0)
        script_content = script_content.replace(echo_line, "")
    else:
        echo_line = "@echo off"

    char_maps = create_char_mappings()

    var_declarations = []
    for mapping in char_maps:
        for char, var in mapping.items():
            var_declarations.append(f"set {var}={char}")
    var_declarations = "&".join(var_declarations)

    script_content = replace_chars_with_vars(script_content, char_maps)

    code_blocks = split_into_blocks(script_content)
    script_content = add_fake_jumps(code_blocks)

    obfuscated_lines = []
    for line in script_content.splitlines():
        if line.strip() == "":
            obfuscated_lines.append("")
            continue

        if re.match(r"^\s*:[a-zA-Z0-9_]+", line) or re.match(r"^\s*goto\s+[a-zA-Z0-9_]+", line, re.IGNORECASE):
            obfuscated_lines.append(line)
            continue

        parts = re.split(r"(%[^%]+%)", line)
        obfuscated_line = []
        for part in parts:
            if re.match(r"%[^%]+%", part):
                obfuscated_line.append(part)
            else:
                transformed_chars = []
                for char in part:
                    if char.isalpha():
                        transformed_chars.append(f"%{generate_text()}%{char}%{generate_text()}%")
                    elif char.isdigit():
                        transformed_chars.append(f"%{generate_text()}%{char}%{generate_text()}%")
                    else:
                        transformed_chars.append(char)
                obfuscated_line.append("".join(transformed_chars))
        obfuscated_lines.append("".join(obfuscated_line))

        garbage_lines = []
        for _ in range(random.randint(1, 2)):
            garbage_lines.append(f"set {create_var_name()}={create_var_value()}%{generate_text()}%{create_var_value()}%{create_var_value()}%{create_var_value()}%{generate_text()}%{create_var_value()}%{create_var_value()}%{create_var_value()}%{generate_text()}%{create_var_value()}%{create_var_value()}%")
            garbage_lines.append(create_junk_comment())
        obfuscated_lines.extend(garbage_lines)

    obfuscated_lines.insert(0, echo_line)
    obfuscated_lines.insert(1, "\n::severance--obfuscator v3.5\n::severance--obfuscator v3.5\n::severance--obfuscator v3.5\n")
    obfuscated_lines.insert(2, var_declarations)
    return "\n".join(obfuscated_lines)

def process_batch_file(input_file, output_file):
    with open(input_file, 'r') as file:
        original_script = file.read()
    
    obfuscated_script = obfuscate_script(original_script)
    
    with open(output_file, 'w') as file:
        file.write(obfuscated_script)

def main():
    if len(sys.argv) != 2:
        print("Drag and drop a batch file onto this python file (not the console) to obfuscate it.")
        input("Press Enter to exit...")
        return

    input_file = sys.argv[1]
    if not os.path.isfile(input_file):
        print(f"File not found: {input_file}")
        input("Press Enter to exit...")
        return

    filename, extension = os.path.splitext(os.path.basename(input_file))
    output_file = f"{filename}_protected{extension}"

    process_batch_file(input_file, output_file)
    print(f"Obfuscated batch file saved to: {output_file}")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()