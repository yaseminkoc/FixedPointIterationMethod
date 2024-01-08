from flask import Flask, request, jsonify
from sympy import Symbol, simplify, latex
from sympy.parsing.latex import parse_latex

from EquationTransformer import EquationTransformer

app = Flask(__name__)

def fixed_point_iteration(fx, x_0, tol, max_iter):
    x = Symbol('x')
    transformer = EquationTransformer(fx)
    for i in range(len(transformer.transformed_equations)):
        g_x = transformer.transformed_equations[i]
        iterations = []
        # Initialize variables
        x_n = x_0
        iter_count = 0

        while iter_count < max_iter:
            x_n1 = g_x.subs(x, x_n)
            iterations.append(float(x_n1))
            # Check for convergence
            if abs(x_n1 - x_n) < tol or abs(parse_latex(fx).subs(x, x_n)) < tol:
                return {"root": float(x_n1), "iterations": iter_count, "all_iterations": iterations}

            x_n = x_n1
            iter_count += 1

    return {"message": "Did not converge within the maximum number of iterations."}

@app.route('/fixed_point_iteration', methods=['POST'])
def api_fixed_point_iteration():
    data = request.get_json()

    f_x = data.get("function")
    x_0 = data.get("initial_guess")
    tol = data.get("tolerance")
    max_iter = data.get("max_iterations")
    if f_x and x_0 is not None and tol is not None and max_iter is not None:
        result = fixed_point_iteration(f_x, x_0, tol, max_iter)
        return jsonify(result)
    else:
        return jsonify({"error": "Invalid input parameters."})

if __name__ == '__main__':
    app.run(debug=True)
