from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

def LogicEval(p, q, r, expr):
    # Replace variables with their values (word-boundary safe)
    expr = re.sub(r"\bp\b", str(p), expr)
    expr = re.sub(r"\bq\b", str(q), expr)
    expr = re.sub(r"\br\b", str(r), expr)

    # Simplify not expressions
    expr = expr.replace("not True", "False")
    expr = expr.replace("not False", "True")

    # Handle parentheses by evaluating innermost expressions first
    while "(" in expr and ")" in expr:
        # Find the innermost parentheses
        start = expr.rfind("(")
        end = expr.find(")", start)
        if start != -1 and end != -1:
            # Extract the expression inside parentheses
            inner_expr = expr[start+1:end]
            # Recursively evaluate the inner expression
            inner_result = LogicEval(p, q, r, inner_expr)
            # Replace the parenthesized expression with its result
            expr = expr[:start] + str(inner_result) + expr[end+1:]
        else:
            break

    # Split into tokens
    lst = expr.split()

    # Convert tokens into numbers/operators
    def convert(val):
        if val == "True":
            return 1
        elif val == "False":
            return 0
        elif val == "and":
            return "*"
        elif val == "or":
            return "+"
        elif val == "not":
            return "not"
        else:
            return val

    lst = [convert(x) for x in lst]

    # First handle "not" operations
    i = 0
    while i < len(lst):
        if lst[i] == "not":
            if i + 1 < len(lst) and isinstance(lst[i+1], int):
                lst[i] = 0 if lst[i+1] else 1
                del lst[i+1]
                i = 0  # reset to start to handle chained/preceding nots
            else:
                i += 1
        else:
            i += 1

    # Then handle "and" (*)
    i = 0
    while i < len(lst):
        if lst[i] == "*":
            if i > 0 and i < len(lst) - 1 and isinstance(lst[i-1], int) and isinstance(lst[i+1], int):
                lst[i-1] = 1 if (lst[i-1] and lst[i+1]) else 0
                del lst[i:i+2]
                i = 0  # reset to start
            else:
                i += 1
        else:
            i += 1

    # Then handle "or" (+)
    i = 0
    while i < len(lst):
        if lst[i] == "+":
            if i > 0 and i < len(lst) - 1 and isinstance(lst[i-1], int) and isinstance(lst[i+1], int):
                lst[i-1] = 1 if (lst[i-1] or lst[i+1]) else 0
                del lst[i:i+2]
                i = 0  # reset to start
            else:
                i += 1
        else:
            i += 1

    # Final result
    return bool(lst[0])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.get_json()
        p = data.get('p', False)
        q = data.get('q', False)
        r = data.get('r', False)
        expr = data.get('expr', '')
        
        # Convert string values to boolean
        p = p.lower() == 'true' if isinstance(p, str) else bool(p)
        q = q.lower() == 'true' if isinstance(q, str) else bool(q)
        r = r.lower() == 'true' if isinstance(r, str) else bool(r)
        
        result = LogicEval(p, q, r, expr)
        return jsonify({'result': str(result)})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)