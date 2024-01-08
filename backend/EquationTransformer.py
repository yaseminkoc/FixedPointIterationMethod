from sympy import symbols, simplify, asin, acos, atan, acot, asec, acsc
from sympy.parsing.latex import parse_latex

class EquationTransformer:
    def __init__(self, original_equation_latex):
        x = symbols('x')
        self.original_equation = simplify(parse_latex(original_equation_latex))
        self.transformed_equations = self.process_equation(self.original_equation, True)

    def process_equation(self, equation, first_time=False):
        sections = equation.as_ordered_terms()
        resulting_equation_list = []

        for term in sections:
            term_str = str(term)
            local_eq_list = []

            if not first_time:
                difference = equation - term
                local_eq_list = [eq - difference for eq in resulting_equation_list]
            else:
                dummy_equation = equation - term
                local_eq_list.append(dummy_equation)

            if "x" in term_str:
                term_str, local_eq_list = self.handle_negativity(term_str, local_eq_list, first_time)
                term_str, local_eq_list = self.handle_coefficient(term_str, local_eq_list)
                is_trig, term_str, local_eq_list = self.handle_trigonometric(term_str, local_eq_list)

                if is_trig:
                    new_eq = parse_latex(term_str)
                    local_eq_list = self.process_equation(new_eq, False)
                else:
                    term_str, local_eq_list = self.handle_power(term_str, local_eq_list)

                resulting_equation_list.extend(local_eq_list)

        return resulting_equation_list

    @staticmethod
    def handle_negativity(chosen_term_str, equation_list, first_time=False):
        new_str = chosen_term_str

        if chosen_term_str[0] == "-":
            new_str = chosen_term_str[1:]
            if not first_time:
                equation_list = [-eq for eq in equation_list]
        else:
            if first_time:
                equation_list = [-eq for eq in equation_list]

        return new_str, equation_list

    @staticmethod
    def handle_coefficient(chosen_term_str, equation_list):
        new_str = chosen_term_str
        index_of_first_star = chosen_term_str.find('*')
        index_of_first_x = chosen_term_str.find('x')

        if index_of_first_star != -1 and index_of_first_star < index_of_first_x:
            coefficient_part = chosen_term_str[:index_of_first_star]
            try:
                coefficient_part = float(coefficient_part)
            except ValueError:
                return chosen_term_str, equation_list

            equation_list = [eq / float(coefficient_part) for eq in equation_list]
            new_str = chosen_term_str[index_of_first_star:]

        return new_str, equation_list

    @staticmethod
    def handle_trigonometric(chosen_term_str, equation_list):
        new_str = chosen_term_str
        last_bracket_index = chosen_term_str.rfind(')')
        is_trig = False

        if last_bracket_index != -1 and last_bracket_index + 1 < len(chosen_term_str):
            new_str, equation_list = EquationTransformer.handle_power(chosen_term_str, equation_list)

        trig_functions = ["sin", "cos", "tan", "cot", "sec", "csc"]

        for func in trig_functions:
            if func in chosen_term_str:
                inside_of_brackets = chosen_term_str[chosen_term_str.find('(') + 1:chosen_term_str.find(')')]
                new_str = inside_of_brackets

                trig_func_dict = {
                    "sin": asin,
                    "cos": acos,
                    "tan": atan,
                    "cot": acot,
                    "sec": asec,
                    "csc": acsc
                }

                for i in range(len(equation_list)):
                    equation_list[i] = trig_func_dict[func](equation_list[i])

                is_trig = True
                break

        return is_trig, new_str, equation_list

    @staticmethod
    def handle_power(chosen_term_str, equation_list):
        new_str = chosen_term_str
        splitted = chosen_term_str.split("**")
        dummy_equation_list = []

        if len(splitted) != 1:
            power_part = splitted[-1]
            index_of_power_part = chosen_term_str.find(power_part)
            power_part = float(power_part)

            if power_part == 0:
                equation_list = [1 for _ in equation_list]
            else:
                if power_part % 2 == 0:
                    equation_list = [eq ** (1 / power_part) for eq in equation_list]
                    dummy_equation_list = [-eq for eq in equation_list]

                else:
                    equation_list = [eq ** (1 / power_part) for eq in equation_list]

                equation_list.extend(dummy_equation_list)
            new_str = chosen_term_str[:index_of_power_part + 2]

        return new_str, equation_list

