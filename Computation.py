

import math
import copy
from scipy.optimize import newton


compounding_methods = {
    'Annual': 1,
    'Semi-Annual': 2,
    'Quarterly': 4,
    'Monthly': 12,
    'Continuous': 'Continuous',
    'Custom': 0,
}


def format_numeric_value(value):
    try:
        return f"{float(value):,}" if value != "" else ""
    except Exception:
        return value


class OutlineCalculation:
    def __init__(self, values:dict):
        self.calc = "Outline"
        self.requirements = []
        self.values = copy.deepcopy(values)
        self.missing_values = []
        self.valid = False
        self.attempt_calc_failed = False

    def validate_values(self):
        valid = True
        for item in self.requirements:
            if item not in self.values:
                if self.attempt_calc_failed:
                    print("ERROR, This item is missing:", item)
                    print("This is what entered:", self.values)
                self.missing_values.append(item)
                valid = False
        return valid

    def calculate(self):
        if not self.valid:
            self.attempt_calc_failed = True
            return

    def display_values(self):
        if not self.valid:
            for item in self.missing_values:
                print(f"Missing data for '{item}'.")
            return


class FutureValue(OutlineCalculation):
    def __init__(self, values:dict):
        super().__init__(values)
        self.calc = "Future Value"
        self.requirements = ["Present Value", "Rate", "Periods", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.PV = self.values["Present Value"]
            self.rate = self.values["Rate"]
            self.periods = self.values["Periods"]
            self.compound = self.values["Compound Method"]
            self.custom = self.values.get("Custom", None)

    def calculate(self):
        super().calculate()

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
        self.requirements = ["Future Value", "Rate", "Periods", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.FV = self.values["Future Value"]
            self.rate = self.values["Rate"]
            self.periods = self.values["Periods"]
            self.compound = self.values["Compound Method"]
            self.custom = self.values.get("Custom", None)

    def calculate(self):
        super().calculate()

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
        self.requirements = ["Cashflow", "Rate", "Start Year", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.cf_list = self.values["Cashflow"]
            self.rate = self.values["Rate"]
            self.starting = self.values["Start Year"]
            self.compound = self.values["Compound Method"]
            self.custom = self.values.get("Custom", None)

    def calculate(self):
        super().calculate()

        i = 0
        present_accumulative = 0
        for cash in self.cf_list:
            self.values["Future Value"] = cash
            self.values["Periods"] = self.starting + i
            try:
                present_accumulative += PresentValue(self.values).calculate()
            except Exception:
                print(self.values)
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
        self.requirements = ["Cashflow", "Start Year"]
        self.valid = self.validate_values()
        if self.valid:
            self.cf_list = self.values["Cashflow"]
            self.starting = self.values["Start Year"]

    def calculate(self):
        super().calculate()

        def calculate_irr(rate):
            return sum([cf / ((1 + rate) ** (year + self.values["Start Year"]))
                        for year, cf in enumerate(self.values['Cashflow'])])
        answer = newton(calculate_irr, 0.10)
        print(f'The Rate in Percentage rounded to 2 decimal places is {round(answer * 100, 2)}%')
        return str(answer) + f' or {round(answer * 100, 2)}%'


    def display_values(self):
        super().display_values()
        bold_name = "\033[1m" + "Calculating Internal Rate" + "\033[0m"
        print(f'{bold_name:~^50}')
        print(f'Cashflow: {self.cf_list}')
        print(f'Starting Year: {format_numeric_value(self.starting)}')


class NominalRate(OutlineCalculation):
    def __init__(self, values:dict):
        super().__init__(values)
        self.calc = "Nominal Rate"
        self.requirements = ["Effective Rate", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.ER = self.values["Effective Rate"]
            self.compound = self.values["Compound Method"]

    def calculate(self):
        super().calculate()
        compounding = compounding_methods[self.compound]
        if compounding != "Continuous":
            def equation(rate):
                return (1 + (rate / compounding))**compounding - 1 - self.ER
            r = newton(equation, 0.10)
        else:
            r = math.log(self.ER + 1)

        return r


    def display_values(self):
        super().display_values()
        bold_name = "\033[1m" + "Calculating Nominal Annual Rate" + "\033[0m"
        print(f'{bold_name:~^50}')
        print(f'Effective Rate: {self.ER * 100}%')
        print(f'Compound Method: {format_numeric_value(self.compound)}')


class PaymentLoan(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Payments for Loan"
        self.requirements = ["Principal", "Periods", "Rate", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.p = self.values["Principal"]
            self.periods = self.values["Periods"]
            self.rate = self.values["Rate"]
            self.compound = self.values["Compound Method"]

    def calculate(self):
        super().calculate()
        compounding = compounding_methods[self.compound]
        r = self.rate / compounding
        n = compounding * self.periods
        return (r * (1 + r)**n * self.p) / ((1 + r)**n - 1)


    def display_values(self):
        super().display_values()
        bold_name = "\033[1m" + "Calculating Payments Needed For Loan" + "\033[0m"
        print(f'{bold_name:~^50}')
        print(f'Principal: {format_numeric_value(self.p)}')
        print(f'Interest Rate: {self.rate * 100}%')
        print(f'Periods: {format_numeric_value(self.periods)}')
        print(f'Compound Method: {format_numeric_value(self.compound)}')


class PerpetualValue(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Perpetual Value"
        self.requirements = ["Perpetual Value", "Rate"]
        self.valid = self.validate_values()
        if self.valid:
            self.prp = self.values["Perpetual Value"]
            self.rate = self.values["Rate"]

    def calculate(self):
        super().calculate()
        return str(self.prp / self.rate) + " in Present Value"


    def display_values(self):
        super().display_values()
        bold_name = "\033[1m" + "Calculating Perpetual Value in Present Value" + "\033[0m"
        print(f'{bold_name:~^50}')
        print(f'Perpetual Value Annually: {format_numeric_value(self.prp)}')
        print(f'Interest Rate: {self.rate * 100}%')


class PrincipalRemaining(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Principal Remaining"
        self.requirements = ["Payments", "Periods", "Rate", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.pay = self.values["Payments"]
            self.periods = self.values["Periods"]
            self.rate = self.values["Rate"]
            self.compound = self.values["Compound Method"]

    def calculate(self):
        super().calculate()
        compounding = compounding_methods[self.compound]
        r = self.rate / compounding
        n = compounding * self.periods
        return (self.pay / r) * (1 - 1/((1+r)**n))

    def display_values(self):
        super().display_values()
        bold_name = "\033[1m" + "Calculating Remaining Principal" + "\033[0m"
        print(f'{bold_name:~^50}')
        print(f'Payments: {format_numeric_value(self.pay)}')
        print(f'Interest Rate: {self.rate * 100}%')
        print(f'Periods: {format_numeric_value(self.periods)}')
        print(f'Compound Method: {format_numeric_value(self.compound)}')


calculation_key = {
    "Future Value": FutureValue,
    "Present Value": PresentValue,
    "Cashflow": CashflowValue,
    "Internal Rate": InternalRate,
    "Nominal Rate": NominalRate,
    "Payments for Loan": PaymentLoan,
    "Principal Remaining": PrincipalRemaining,
    "Perpetual Value": PerpetualValue
}