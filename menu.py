import math
import sympy as sp

possible_calculation = {
    "Future Value": ["Present Value", "Rate", "Periods", "Compound Method"],
    "Present Value": ["Future Value", "Rate", "Periods", "Compound Method"],
    "Cashflow": ["Cashflow", "Rate", "Start Year", "Compound Method"]
}


def format_numeric_value(value):
    try:
        return f"{float(value):,}" if value != "" else ""
    except Exception:
        return value

class OutlineCalculation:
    def __init__(self, values:dict):
        self.calc = "Outline"
        self.values = values
        self.missing_values = []

    def validate_values(self):
        required_items = possible_calculation.get(self.calc, [])
        valid = True
        for item in required_items:
            if item not in self.values:
                self.missing_values.append(item)
                valid = False
        return valid


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

    def calculate_future_value(self):
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
        if not self.valid:
            for item in self.missing_values:
                print(f"Missing data for '{item}'.")
            return
        bold_name = "\033[1m" + "Calculating Future Value" + "\033[0m"
        print(f'{bold_name:~^40}')
        print(f'Present Value: {format_numeric_value(self.values["Present Value"])}')
        print(f'Interest Rate Percent:" {self.values["Rate"] * 100}%')
        print(f'Periods:" {format_numeric_value(self.values["Periods"])}')
        print(f'Compound Method:" {format_numeric_value(self.values["Compound Method"])}')

# Usage example:
values_present_value = {
    "Present Value": 1000,
    "Rate": 0.05,
    "Periods": 5,
    "Compound Method": "Annual"
}
pv = FutureValue(values_present_value)
pv.display_values()
print(f'Present Value: {pv.calculate_future_value()}')
