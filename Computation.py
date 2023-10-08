

import math
import copy
import sympy as sp


def format_numeric_value(value):
    try:
        return f"{float(value):,}" if value != "" else ""
    except Exception:
        return value


class OutlineCalculation:
    def __init__(self, values:dict):
        self.calc = "Outline"
        self.values = copy.copy(values)
        self.missing_values = []
        self.valid = False

    def validate_values(self):
        required_items = possible_calculation.get(self.calc, [])
        valid = True
        for item in required_items:
            if item not in self.values:
                self.missing_values.append(item)
                valid = False
        return valid

    def display_values(self):
        if not self.valid:
            for item in self.missing_values:
                print(f"Missing data for '{item}'.")
            return


class FutureValue(OutlineCalculation):
    def __init__(self, values:dict):
        super().__init__(values)
        self.calc = "Future Value"
        self.valid = self.validate_values()
        if self.valid:
            self.PV = self.values["Present Value"]
            self.rate = self.values["Rate"]
            self.periods = self.values["Periods"]
            self.compound = self.values["Compound Method"]
            self.custom = self.values.get("Custom", None)

    def calculate(self):
        if not self.valid:
            return

        if self.compound == "Annual":
            return self.PV * (1 + self.rate) ** self.periods
        elif self.compound == "Semi-Annual":
            return self.PV * (1 + self.rate/2) ** (self.periods * 2)
        elif self.compound == "Quarterly":
            return self.PV * (1 + self.rate/4) ** (self.periods * 4)
        elif self.compound == "Monthly":
            return self.PV * (1 + self.rate/12) ** (self.periods * 12)
        elif self.compound == "Continuous":
            return self.PV * math.e ** (self.rate * self.periods)
        elif self.compound == "Custom":
            return self.PV * (1 + self.rate/self.custom) ** (self.periods * self.custom)

    def display_values(self):
        super().display_values()
        bold_name = "\033[1m" + "Calculating Future Value" + "\033[0m"
        print(f'{bold_name:~^40}')
        print(f'Present Value: {format_numeric_value(self.PV)}')
        print(f'Interest Rate Percent:" {self.rate * 100}%')
        print(f'Periods:" {format_numeric_value(self.periods)}')
        print(f'Compound Method:" {format_numeric_value(self.compound)}')


class PresentValue(OutlineCalculation):
    def __init__(self, values:dict):
        super().__init__(values)
        self.calc = "Present Value"
        self.valid = self.validate_values()
        if self.valid:
            self.FV = self.values["Future Value"]
            self.rate = self.values["Rate"]
            self.periods = self.values["Periods"]
            self.compound = self.values["Compound Method"]
            self.custom = self.values.get("Custom", None)

    def calculate(self):
        if self.compound == "Annual":
            return self.FV / (1 + self.rate) ** self.periods
        elif self.compound == "Semi-Annual":
            return self.FV / (1 + self.rate / 2) ** (self.periods * 2)
        elif self.compound == "Quarterly":
            return self.FV / (1 + self.rate / 4) ** (self.periods * 4)
        elif self.compound == "Monthly":
            return self.FV / (1 + self.rate / 12) ** (self.periods * 12)
        elif self.compound == "Continuous":
            return self.FV / (math.e ** (self.rate * self.periods))
        elif self.compound == "Custom":
            return self.FV / ((1 + self.rate / self.custom) ** (self.periods * self.custom))

    def display_values(self):
        super().display_values()
        bold_name = "\033[1m" + "Calculating Present Value" + "\033[0m"
        print(f'{bold_name:~^40}')
        print(f'Future Value: {format_numeric_value(self.FV)}')
        print(f'Interest Rate Percent: {self.rate * 100}%')
        print(f'Periods: {format_numeric_value(self.periods)}')
        print(f'Compound Method: {format_numeric_value(self.compound)}')


class CashflowValue(OutlineCalculation):
    def __init__(self, values:dict):
        super().__init__(values)
        self.calc = "Cashflow"
        self.valid = self.validate_values()
        if self.valid:
            self.cf_list = self.values["Cashflow"]
            self.rate = self.values["Rate"]
            self.starting = self.values["Start Year"]
            self.compound = self.values["Compound Method"]
            self.custom = self.values.get("Custom", None)

    def calculate(self):
        i = 0
        present_accumulative = 0
        for cash in self.cf_list:
            self.values["Present Value"] = cash
            self.values["Periods"] = self.starting + i
            present_accumulative += PresentValue(self.values)
            i += 1
        return str(format_numeric_value(present_accumulative)) + " in Present Value"

    def display_values(self):
        super().display_values()
        bold_name = "\033[1m" + "Calculating Present Value of Cashflow" + "\033[0m"
        print(f'{bold_name:~^50}')
        print(f'Cashflow: {self.cf_list}')
        print(f'Interest Rate Percent: {self.rate * 100}%')
        print(f'Starting Year: {format_numeric_value(self.starting)}')
        print(f'Compound Method: {format_numeric_value(self.compound)}')


class InternalRate(OutlineCalculation):
    def __init__(self, values:dict):
        super().__init__(values)
        self.calc = "Internal Rate"
        self.valid = self.validate_values()
        if self.valid:
            self.cf_list = self.values["Cashflow"]
            self.starting = self.values["Start Year"]

    def calculate(self):
        starting_point = self.values['Start Year']
        c = sp.symbols('c')
        equation = sum(coeff * c ** (i + starting_point)
                       for i, coeff in enumerate(self.values['Cashflow']))
        roots = sp.solve(equation, c)
        real_roots = [root.evalf() for root in roots if root.is_real]
        answer = []
        for c in real_roots:
            answer.append((1/c) - 1)

        if len(answer) == 1:
            return answer[0]
        else:
            for rate in answer:
                print(f'Rate: {rate}')
            return "above"

    def display_values(self):
        super().display_values()
        bold_name = "\033[1m" + "Calculating Internal Rate" + "\033[0m"
        print(f'{bold_name:~^50}')
        print(f'Cashflow: {self.cf_list}')
        print(f'Starting Year: {format_numeric_value(self.starting)}')


possible_calculation = {
    "Future Value": ["Present Value", "Rate", "Periods", "Compound Method"],
    "Present Value": ["Future Value", "Rate", "Periods", "Compound Method"],
    "Cashflow": ["Cashflow", "Rate", "Start Year", "Compound Method"],
    "Internal Rate": ["Cashflow"]
}

calculation_class_key = {
    "Future Value": FutureValue,
    "Present Value": PresentValue,
    "Cashflow": CashflowValue,
    "Internal Rate": InternalRate
}