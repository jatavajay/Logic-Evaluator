from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

def LogicEval(p, q, r, expr):
    """Evaluate logical expression with variables p, q, r"""
    try:
        # Create variable mapping
        variables = {
            'p': bool(p),
            'q': bool(q),
            'r': bool(r)
        }
        
        print(f"Debug: p={p}, q={q}, r={r}")
        print(f"Debug: Original expr: {expr}")
        
        # First substitute variables in the expression
        expr_substituted = substitute_variables(expr, variables)
        print(f"Debug: After substitution: {expr_substituted}")
        
        # Evaluate the substituted expression
        result = evaluate_logical_expression(expr_substituted)
        print(f"Debug: Result: {result}")
        
        return bool(result)
        
    except Exception as e:
        print(f"Debug: Evaluation error: {e}")
        return False

def substitute_variables(expr, variables):
    """Replace variables with their boolean values in the expression"""
    # Replace variables with True/False
    for var, value in variables.items():
        # Use word boundaries to avoid partial replacements
        import re
        pattern = r'\b' + var + r'\b'
        replacement = 'True' if value else 'False'
        expr = re.sub(pattern, replacement, expr)
    
    return expr

def evaluate_logical_expression(expr):
    """Safely evaluate a logical expression containing only True, False, and, or, not, parentheses"""
    try:
        # Clean the expression
        expr = expr.strip()
        
        # Replace logical operators with Python equivalents
        expr = expr.replace(' and ', ' and ')
        expr = expr.replace(' or ', ' or ')
        expr = expr.replace(' not ', ' not ')
        
        # Ensure proper spacing around operators
        import re
        expr = re.sub(r'\band\b', ' and ', expr)
        expr = re.sub(r'\bor\b', ' or ', expr)
        expr = re.sub(r'\bnot\b', ' not ', expr)
        
        # Only allow safe characters and keywords
        allowed_chars = set('TrueFalse andornot()' + ' ')
        if not all(c in allowed_chars for c in expr):
            raise ValueError("Invalid characters in expression")
        
        # Only allow specific keywords
        allowed_words = {'True', 'False', 'and', 'or', 'not'}
        words = re.findall(r'\b\w+\b', expr)
        if not all(word in allowed_words for word in words):
            raise ValueError("Invalid keywords in expression")
        
        # Safely evaluate the expression
        result = eval(expr, {"__builtins__": {}}, {"True": True, "False": False, "and": lambda x, y: x and y, "or": lambda x, y: x or y, "not": lambda x: not x})
        
        return bool(result)
        
    except Exception as e:
        print(f"Evaluation error: {e}")
        return False

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
        p = data.get('p', False)
        q = data.get('q', False)
        r = data.get('r', False)
        expr = data.get('expr', '')
        
        p = p.lower() == 'true' if isinstance(p, str) else bool(p)
        q = q.lower() == 'true' if isinstance(q, str) else bool(q)
        r = r.lower() == 'true' if isinstance(r, str) else bool(r)
        
        expr = expr.strip()
        result = LogicEval(p, q, r, expr)
        return jsonify({'result': str(result)})
    except Exception as e:
        return jsonify({'error': f'Evaluation error: {str(e)}'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
