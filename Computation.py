

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
        self.valid = self.validate_values()

    def validate_values(self):
        required_items = possible_calculation.get(self.calc, [])
        valid = True
        for item in required_items:
            if item not in self.values:
                self.missing_values.append(item)
                valid = False
        return valid


class FutureValue(OutlineCalculation):
    def validate_values(self):
        self.calc = "Future Value"
        super().validate_values()
        if self.valid:
            self.PV = self.values["Present Value"]
            self.rate = self.values["Rate"]
            self.periods = self.values["Periods"]
            self.compound = self.values["Compound Method"]
            self.custom = self.values.get("Custom", [])


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
        print(f'{bold_name:^30}')
        print(f'Present Value: {format_numeric_value(self.values["Present Value"])}')
        print(f'Interest Rate Percent:" {self.values["Rate"] * 100}%')
        print(f'Periods:" {format_numeric_value(self.values["Periods"])}')
        print(f'Compound Method:" {format_numeric_value(self.values["Compound Method"])}')





def calculate_present_value(FV, rate, periods, compound="Annual", custom=None):
    if compound == "Annual":
        return FV / (1 + rate) ** periods
    elif compound == "Semi-Annual":
        return FV / (1 + rate/2) ** (periods * 2)
    elif compound == "Quarterly":
        return FV / (1 + rate/4) ** (periods * 4)
    elif compound == "Monthly":
        return FV / (1 + rate/12) ** (periods * 12)
    elif compound == "Continuous":
        return FV / (math.e ** (rate * periods))
    elif compound == "Custom":
        return FV / ((1 + rate/custom) ** (periods * custom))

def calculate_cashflow(cf_list, rate, starting=0, compound="Annual", custom=None):
    i = 0
    present_accumulative = 0
    for cash in cf_list:
        present_accumulative += calculate_present_value(cash, rate, (starting + i), compound, custom)
        i += 1
    return present_accumulative