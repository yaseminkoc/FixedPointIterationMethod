
import tkinter as tk
from tkinter import ttk
import requests
import matplotlib.pyplot as plt
from latex2sympy import latex2sympy
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np
from sympy.parsing.latex import parse_latex

class FixedPointGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Fixed-Point Iteration Visualization")

        self.function_label = ttk.Label(self.master, text="Enter function in LaTeX format:")
        self.function_entry = ttk.Entry(self.master, width=30)

        self.initial_guess_label = ttk.Label(self.master, text="Initial guess:")
        self.initial_guess_entry = ttk.Entry(self.master, width=30)

        self.tol_label = ttk.Label(self.master, text="Tolerance:")
        self.tol_entry = ttk.Entry(self.master, width=30)

        self.max_iter_label = ttk.Label(self.master, text="Max iterations:")
        self.max_iter_entry = ttk.Entry(self.master, width=30)

        self.plot_button = ttk.Button(self.master, text="Run Fixed-Point Iteration", command=self.run_iteration, style="Run.TButton")

        self.function_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.function_entry.grid(row=0, column=1, padx=5, pady=5)

        self.initial_guess_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.initial_guess_entry.grid(row=1, column=1, padx=5, pady=5)

        self.tol_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.tol_entry.grid(row=2, column=1, padx=5, pady=5)

        self.max_iter_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.max_iter_entry.grid(row=3, column=1, padx=5, pady=5)

        self.plot_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.master.configure(background="lightblue")

        style = ttk.Style()
        style.configure("Run.TButton", foreground="black", background="black", font=("Arial", 10, "bold"),
                        highlightbackground="black")
    def run_iteration(self):
        function = self.function_entry.get()
        initial_guess = float(self.initial_guess_entry.get())
        tolerance = float(self.tol_entry.get())
        max_iterations = int(self.max_iter_entry.get())
        data = {
            "function": function,
            "initial_guess": initial_guess,
            "tolerance": tolerance,
            "max_iterations": max_iterations
        }

        response = requests.post("http://127.0.0.1:5000/fixed_point_iteration", json=data)

        if response.status_code == 200:
            result = response.json()
            print(result)
            root = result.get("root")
            iterations = result.get("iterations")
            all_iterations = result.get("all_iterations")

            if root is not None:
                result_message = f"Converged to root {root} in {iterations} iterations."
            else:
                result_message = f"Did not converge within the maximum number of iterations."

            self.plot_iteration(all_iterations, function, result_message)
        else:
            print(f"Error: {response.status_code} - {response.text}")

    def plot_iteration(self, all_iterations, function, result_message):
        fig, ax1 = plt.subplots()

        # Plot the function on the left axis
        x_vals = np.linspace(min(all_iterations), max(all_iterations), 100)

        expr = parse_latex(function)

        y_vals = [expr.subs('x', val) for val in x_vals]
        ax1.plot(x_vals, y_vals, label=f'Function: ${function}$', color='green')

        ax1.set(xlabel='Approximation', ylabel='Function Value', title='Fixed-Point Iteration Process')
        ax1.legend(loc='upper left')
        ax1.grid()

        # Create a secondary axis on the right for iterations
        ax2 = ax1.twinx()
        ax2.set_ylabel('Iteration', color='blue')

        # Clear the previous iterations
        ax2.clear()

        # Plot the latest iteration on the right axis at y = 0
        ax2.plot(all_iterations, np.zeros_like(all_iterations),
                 marker='o', color='blue', label='Fixed-Point Iteration')

       # ax2.legend(loc='upper right')
        ax2.grid()

        canvas = FigureCanvasTkAgg(fig, master=self.master)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=5, column=0, columnspan=2, pady=10)

        result_label = ttk.Label(self.master, text=result_message)
        result_label.grid(row=6, column=0, columnspan=2)

        iteration_label = ttk.Label(self.master, text="Iteration: ")
        iteration_label.grid(row=7, column=0, columnspan=2, pady=5)

        def update(frame):
            # Update the left axis (function plot)
            ax1.clear()
            ax1.plot(x_vals, y_vals, label=f'Function: ${function}$', color='green')
            ax1.set(xlabel='Approximation', ylabel='Function Value', title='Fixed-Point Iteration Process')
            ax1.legend(loc='upper left')
            ax1.grid()

            # Update the right axis (iterations)
            ax2.clear()

            # Plot the latest iteration on the right axis at y = 0
            if frame + 1 < len(all_iterations):
                ax1.plot(all_iterations[frame + 1], np.zeros_like(all_iterations[frame + 1]),
                         marker='o', linestyle='-', color='blue', label='Fixed-Point Iteration')

            ax2.set_ylabel('Iteration', color='blue')
            # ax2.legend(loc='upper right')
            # ax2.grid()

            # Draw a horizontal line at y = 0 on both axes
            ax1.axhline(y=0, color='red', linestyle='--', label='y=0')
           # ax2.axhline(y=0, color='red', linestyle='--', label='y=0')

            # Update the iteration label
            iteration_label.config(text=f"Iteration: {frame}")

        ani = FuncAnimation(fig, update, frames=len(all_iterations), interval=500, repeat=True)

        # Replace plt.show() with canvas.draw()
        canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = FixedPointGUI(root)
    root.mainloop()

