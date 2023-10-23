

import math
import copy
from scipy.optimize import newton


values_dict = {
    1: ("Present Value", "commas"),  #  Commas Allowed
    2: ("Future Value", "commas"),
    3: ("Cashflow", "cf"),           #  Cashflow Entry is Unique
    0: ("Return", "return")
}

rates_dict = {
    1: ("Interest Rate", "percent"),   #  Percentage Entry,
    2: ("Effective Rate", "percent"),
    3: ("Nominal Rate", "percent"),
    4: ("Periods", "commas"),
    0: ("Return", "return")
}

loans_dict = {
    1: ("Principal", "commas"),
    2: ("Payments", "commas"),
    3: ("Perpetual Value", "commas"),
    0: ("Return", "return")
}

bonds_dict = {
    1: ("Face Value", "commas"),
    2: ("Coupons", "commas"),
    3: ("Yield", "percent"),
    4: ("Coupons per Period", "commas"),
    5: ("Periods", "commas"),
    6: ("Bond Price", "commas"),
    0: ("Return", "return")
}

extra_format_storage = {
    0: ("Compound Method", "commas")  # default is commas
}

menu_layout = {
    1: ("Value", values_dict),  # Present Value, Future Value, Cashflow
    2: ("Rate", rates_dict),   # Interest Rate, Effective Rate, Nominal Rate
    3: ("Loan", loans_dict),
    4: ("Bond", bonds_dict),
    0: "Complete"
}

ingredients_catalog = {}
for dictionary in [values_dict, rates_dict, bonds_dict, extra_format_storage]:
    for tup in dictionary.values():
        if len(tup) == 2:
            ingredients_catalog[tup[0]] = tup[1]
        elif len(tup) == 3:
            ingredients_catalog[tup[0]] = (tup[1], tup[2])

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
        self.title = "Custom Title"
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
        bold_name = "\033[1m" + f"Calculating {self.title}" + "\033[0m"
        print(f'{bold_name:~^40}')
        for item in self.values:
            if item in ingredients_catalog and item in self.requirements:
                if ingredients_catalog[item] == "commas":
                    print(f'{item}: {format_numeric_value(self.values[item])}')
                elif ingredients_catalog[item] == "percent":
                    print(f'{item}: {self.values[item] * 100}%')
                elif ingredients_catalog[item] == "cf":
                    print(f'{item}: {self.values[item]}')
                else:
                    print(f'Failed to file-- {item}: {self.values[item]}')
            elif item in ingredients_catalog:
                pass
            else:
                print(f"Uncatalogued-- {item}: {self.values[item]}")


class FutureValue(OutlineCalculation):
    def __init__(self, values:dict):
        super().__init__(values)
        self.calc = "Future Value"
        self.requirements = ["Present Value", "Interest Rate", "Periods", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.PV = self.values["Present Value"]
            self.rate = self.values["Interest Rate"]
            self.periods = self.values["Periods"]
            self.compound = self.values["Compound Method"]
            self.custom = self.values.get("Custom", None)

    def calculate(self):
        super().calculate()
        periods = compounding_methods[self.compound]
        if self.compound not in ("Continuous", "Custom"):
            return self.PV * (1 + self.rate / periods) ** (self.periods * periods)
        elif self.compound == "Continuous":
            return self.PV * math.e ** (self.rate * self.periods)
        elif self.compound == "Custom":
            return self.PV * (1 + self.rate/self.custom) ** (self.periods * self.custom)


class PresentValue(OutlineCalculation):
    def __init__(self, values:dict):
        super().__init__(values)
        self.calc = "Present Value"
        self.title = "Present Value from Future Value"
        self.requirements = ["Future Value", "Interest Rate", "Periods", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.FV = self.values["Future Value"]
            self.rate = self.values["Interest Rate"]
            self.periods = self.values["Periods"]
            self.compound = self.values["Compound Method"]
            self.custom = self.values.get("Custom", None)

    def calculate(self):
        super().calculate()
        periods = compounding_methods[self.compound]
        if self.compound not in ("Continuous", "Custom"):
            return self.FV / (1 + self.rate / periods) ** (self.periods * periods)
        elif self.compound == "Continuous":
            return self.FV / (math.e ** (self.rate * self.periods))
        elif self.compound == "Custom":
            return self.FV / ((1 + self.rate / self.custom) ** (self.periods * self.custom))


class CashflowValue(OutlineCalculation):
    def __init__(self, values:dict):
        super().__init__(values)
        self.calc = "Cashflow"
        self.title = "Present Value of Cashflow"
        self.requirements = ["Cashflow", "Interest Rate", "Start Year", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.cf_list = self.values["Cashflow"]
            self.rate = self.values["Interest Rate"]
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


class InternalRate(OutlineCalculation):
    def __init__(self, values:dict):
        super().__init__(values)
        self.calc = "Internal Rate"
        self.title = "Internal Rate"
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


class NominalRate(OutlineCalculation):
    def __init__(self, values:dict):
        super().__init__(values)
        self.calc = "Nominal Rate"
        self.title = "Nominal Annual Rate"
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


class PaymentLoan(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Payments for Loan"
        self.title = "Payments Needed For Loan"
        self.requirements = ["Principal", "Periods", "Interest Rate", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.p = self.values["Principal"]
            self.periods = self.values["Periods"]
            self.rate = self.values["Interest Rate"]
            self.compound = self.values["Compound Method"]

    def calculate(self):
        super().calculate()
        compounding = compounding_methods[self.compound]
        r = self.rate / compounding
        n = compounding * self.periods
        return (r * (1 + r)**n * self.p) / ((1 + r)**n - 1)


class PerpetualValue(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Perpetual Value"
        self.requirements = ["Perpetual Value", "Interest Rate"]
        self.valid = self.validate_values()
        if self.valid:
            self.prp = self.values["Perpetual Value"]
            self.rate = self.values["Interest Rate"]

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
        self.title = "Remaining Principal"
        self.requirements = ["Payments", "Periods", "Interest Rate", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.pay = self.values["Payments"]
            self.periods = self.values["Periods"]
            self.rate = self.values["Interest Rate"]
            self.compound = self.values["Compound Method"]

    def calculate(self):
        super().calculate()
        compounding = compounding_methods[self.compound]
        r = self.rate / compounding
        n = compounding * self.periods
        return (self.pay / r) * (1 - 1 / ((1+r) ** n))

#  principal remaining seems off
#  add feature to find principal remaining w/o Payments since can be calculated without
#  separate calc into more modules to clean code

class BondPrice(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Bond Price"
        self.title = "Bond Price in Present Value"
        self.requirements = ["Face Value", "Coupons", "Coupons per Period", "Yield",
                             "Periods"]
        self.valid = self.validate_values()
        if self.valid:
            self.fv = self.values["Face Value"]
            self.coup = self.values["Coupons"]
            self.m = self.values["Coupons per Period"]
            self.y = self.values["Yield"]
            self.periods = self.values["Periods"]

    def calculate(self):
        super().calculate()
        n = self.m * self.periods
        if self.m <= 10000:
            present_value_fv = self.fv / ((1 + (self.y / self.m )) ** n)
            present_value_coup = (self.coup / self.y) * (1 - (1 / (1 + (self.y / self.m )) ** n))
            return present_value_fv + present_value_coup
        else:
            fract_1 = 1 / (math.e ** (self.y * self.periods))
            fract_2 = self.fv + ((self.coup / self.y) * (math.e ** (self.y * self.periods) - 1))
            return fract_1 * fract_2


class YieldToMaturity(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Yield To Maturity"
        self.title = "Finding Yield To Maturity in Percent"
        self.requirements = ["Face Value", "Coupons", "Coupons per Period", "Bond Price",
                             "Periods"]
        self.valid = self.validate_values()
        if self.valid:
            self.fv = self.values["Face Value"]
            self.coup = self.values["Coupons"]
            self.m = self.values["Coupons per Period"]
            self.bp = self.values["Bond Price"]
            self.periods = self.values["Periods"]

    def calculate(self):
        super().calculate()
        ytm = .1  # initial ytm guess before bisect alg
        lower_bound = -1
        upper_bound = 1
        tolerance = 0.000001
        for i in range(100):
            self.values["Yield"] = ytm
            guessed_bond_price = BondPrice(self.values).calculate()
            if abs(guessed_bond_price - self.bp) > tolerance:
                if guessed_bond_price < self.bp:
                    upper_bound = ytm
                    ytm = (ytm + lower_bound) / 2
                elif guessed_bond_price > self.bp:
                    lower_bound = ytm
                    ytm = (ytm + upper_bound) / 2
            else:
                return f"{ytm * 100}%"
        else:
            return "Outside of Upper and Lower Bounds"


class MacaulayDuration(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Macaulay Duration"
        self.title = "Macaulay Duration aka How Many Payments/Periods Left"
        self.requirements = ["Face Value", "Coupons", "Coupons per Period", "Yield",
                             "Periods"]
        self.valid = self.validate_values()
        if self.valid:
            self.fv = self.values["Face Value"]
            self.coup = self.values["Coupons"]  # Called % Coupon Bonds or % Bond
            self.m = self.values["Coupons per Period"]
            self.y = self.values["Yield"]  # Yield or Bond Yielding %
            self.periods = self.values["Periods"]

    def calculate(self):
        super().calculate()
        n = self.m * self.periods
        c = (self.coup / self.fv) / self.m
        y = self.y / self.m
        fract_1 = (1 + y) / (self.m * y)
        fract_2 = (1 + y + n * (c - y)) / (self.m * c * ((1 + y) ** n - 1) + self.m * y)
        return fract_1 - fract_2


class ModifiedDuration(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Modified Duration"
        self.title = "Modified Duration also known as Sensitivity"
        self.requirements = ["Face Value", "Coupons", "Coupons per Period", "Yield",
                             "Periods"]
        self.valid = self.validate_values()
        if self.valid:
            self.fv = self.values["Face Value"]
            self.coup = self.values["Coupons"]  # Called % Coupon Bonds or % Bond
            self.m = self.values["Coupons per Period"]
            self.y = self.values["Yield"]  # Yield or Bond Yielding %
            self.periods = self.values["Periods"]

    def calculate(self):
        super().calculate()
        P = BondPrice(self.values).calculate()
        D = MacaulayDuration(self.values).calculate()
        answer = (1 / (1 + self.y / self.m)) * D
        return str(answer) + f" or {answer:.2f} payments aka periods left."



calculation_key = {
    "Future Value": FutureValue,
    "Present Value": PresentValue,
    "Cashflow": CashflowValue,
    "Internal Rate": InternalRate,
    "Nominal Rate": NominalRate,
    "Payments for Loan": PaymentLoan,
    "Principal Remaining": PrincipalRemaining,
    "Perpetual Value": PerpetualValue,
    "Bond Price": BondPrice,   # Slightly off by .3%                    P and lamda should be switchable
    "Macaulay Duration": MacaulayDuration,   # Slightly off by 1%
    "Modified Duration": ModifiedDuration,
    "Yield To Maturity": YieldToMaturity
}