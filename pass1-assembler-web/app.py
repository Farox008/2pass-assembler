from flask import Flask, request, jsonify
import os

app = Flask(__name__, static_url_path='', static_folder='static')


# Path to store uploaded files temporarily
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/run_pass1', methods=['POST'])
def run_pass1():
    # Ensure that files are being received properly
    if 'inputFile' not in request.files or 'optabFile' not in request.files:
        return jsonify({'error': 'Missing files'}), 400

    input_file = request.files['inputFile']
    optab_file = request.files['optabFile']

    # Save the uploaded files
    input_path = os.path.join(UPLOAD_FOLDER, 'input.txt')
    optab_path = os.path.join(UPLOAD_FOLDER, 'optab.txt')

    input_file.save(input_path)
    optab_file.save(optab_path)

    # Run pass1 assembler logic
    intermediate, symtab = run_pass1_assembler(input_path, optab_path)

    return jsonify({
        'intermediateFile': "\n".join(intermediate),
        'symbolTable': "\n".join(symtab)
    })


def run_pass1_assembler(input_path, optab_path):
    locctr = 0
    symtab = {}
    intermediate_lines = []
    optab = {}

    # Read the Opcode Table (OPTAB)
    with open(optab_path, 'r') as f:
        for line in f:
            mnemonic, machine_code = line.strip().split()
            optab[mnemonic] = machine_code

    # Process the input file for Pass One
    with open(input_path, 'r') as fin:
        for line in fin:
            line = line.strip().split()

            # Handle line format (either with or without label)
            if len(line) == 3:
                label, opcode, operand = line
            else:
                label = None
                opcode, operand = line
            
            # Handle START directive
            if opcode == 'START':
                locctr = int(operand, 16)  # Convert operand to hexadecimal
                intermediate_lines.append(f"{locctr:04X}\t{label or ''}\t{opcode}\t{operand}")
                continue  # Skip to the next line after handling START

            # Add to intermediate file representation
            intermediate_lines.append(f"{locctr:04X}\t{label or ''}\t{opcode}\t{operand}")
            
            # Add label to SYMTAB if it's not a duplicate
            if label and label not in symtab:
                symtab[label] = locctr

            # Update LOCCTR based on instruction or directive
            if opcode in optab:
                locctr += 3  # Assuming all machine instructions take 3 bytes
            elif opcode == 'WORD':
                locctr += 3
            elif opcode == 'RESW':
                locctr += 3 * int(operand)
            elif opcode == 'RESB':
                locctr += int(operand)
            elif opcode == 'BYTE':
                if operand.startswith('C'):
                    locctr += len(operand) - 3  # Length of character constant
                elif operand.startswith('X'):
                    locctr += (len(operand) - 3) // 2  # Length of hex constant
            elif opcode == 'END':
                break

    # Convert SYMTAB to list of strings for output
    symtab_lines = [f"{label}\t{locctr:04X}" for label, locctr in symtab.items()]
    
    return intermediate_lines, symtab_lines


# Start Flask app
if __name__ == '__main__':
    app.run(debug=True)
