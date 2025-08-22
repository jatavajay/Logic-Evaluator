from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

def LogicEval(p, q, r, expr):
    # Debug print
    print(f"Evaluating: p={p}, q={q}, r={r}, expr='{expr}'")
    
    # Replace variables with their values
    expr = expr.replace("p", str(p))
    expr = expr.replace("q", str(q))
    expr = expr.replace("r", str(r))
    
    # Convert to tokens with proper handling of parentheses
    tokens = tokenize(expr)
    
    # Evaluate the expression
    result = evaluate_expression(tokens)
    return result

def tokenize(expr):
    """Convert expression string into tokens"""
    # Add spaces around operators and parentheses for proper splitting
    expr = expr.replace('(', ' ( ')
    expr = expr.replace(')', ' ) ')
    expr = expr.replace('not', ' not ')
    expr = expr.replace('and', ' and ')
    expr = expr.replace('or', ' or ')
    
    # Split and filter out empty strings
    tokens = [token for token in expr.split() if token]
    return tokens

def evaluate_expression(tokens):
    """Evaluate tokenized expression with proper operator precedence and parentheses"""
    # Convert tokens to values and operators
    parsed_tokens = []
    for token in tokens:
        if token == 'True':
            parsed_tokens.append(True)
        elif token == 'False':
            parsed_tokens.append(False)
        elif token in ('and', 'or', 'not', '(', ')'):
            parsed_tokens.append(token)
        else:
            if isinstance(token, bool):
                parsed_tokens.append(token)
            else:
                parsed_tokens.append(False)
    
    def eval_parentheses(tokens):
        stack = []
        for token in tokens:
            if token == ')':
                inner_expr = []
                while stack and stack[-1] != '(':
                    inner_expr.append(stack.pop())
                if stack and stack[-1] == '(':
                    stack.pop()
                inner_expr.reverse()
                result = eval_operators(inner_expr)
                stack.append(result)
            else:
                stack.append(token)
        return stack
    
    def eval_operators(tokens):
        tokens = eval_not(tokens)
        tokens = eval_and(tokens)
        tokens = eval_or(tokens)
        return tokens[0] if len(tokens) == 1 else False
    
    def eval_not(tokens):
        result = []
        i = 0
        while i < len(tokens):
            if tokens[i] == 'not':
                if i + 1 < len(tokens):
                    result.append(not tokens[i + 1])
                    i += 2
                else:
                    result.append(False)
                    i += 1
            else:
                result.append(tokens[i])
                i += 1
        return result
    
    def eval_and(tokens):
        result = []
        i = 0
        while i < len(tokens):
            if i + 2 < len(tokens) and tokens[i + 1] == 'and':
                left = tokens[i]
                right = tokens[i + 2]
                result.append(left and right)
                i += 3
            else:
                result.append(tokens[i])
                i += 1
        return result
    
    def eval_or(tokens):
        result = []
        i = 0
        while i < len(tokens):
            if i + 2 < len(tokens) and tokens[i + 1] == 'or':
                left = tokens[i]
                right = tokens[i + 2]
                result.append(left or right)
                i += 3
            else:
                result.append(tokens[i])
                i += 1
        return result
    
    tokens_after_parentheses = eval_parentheses(parsed_tokens)
    final_result = eval_operators(tokens_after_parentheses)
    return bool(final_result)

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading template: {str(e)}. Please check if templates/index.html exists."

@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        p = data.get('p', False)
        q = data.get('q', False)
        r = data.get('r', False)
        expr = data.get('expr', '')
        
        # Convert to boolean (handle both string and boolean inputs)
        if isinstance(p, str):
            p = p.lower() == 'true'
        if isinstance(q, str):
            q = q.lower() == 'true'
        if isinstance(r, str):
            r = r.lower() == 'true'
        
        p = bool(p)
        q = bool(q)
        r = bool(r)
        
        print(f"Boolean values - p: {p}, q: {q}, r: {r}")
        print(f"Expression: {expr}")
        
        result = LogicEval(p, q, r, expr)
        print(f"Result: {result}")
        
        return jsonify({'result': str(result)})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': f'Evaluation error: {str(e)}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
