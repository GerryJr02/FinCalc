

import math
import copy
from scipy.optimize import newton
import numpy as np
from pulp import LpMaximize, LpProblem, LpVariable, lpSum
from scipy.optimize import linprog


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
    5: ("Compound Method", "comp"),
    6: ("First Spot Year", "sp1"),
    7: ("Second Spot Year", "sp2"),
    8: ("Forward Rate", "percent only"),
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
    3: ("Yield", "percent only"),
    4: ("Coupons per Period", "commas"),
    5: ("Periods", "commas"),
    6: ("Bond Price", "commas"),
    7: ("New Yield", "percent only"),
    8: ("Spot Rate List", "sp_lst"),
    0: ("Return", "return")
}

extra_format_storage = {
    0: ("Compound Method", "commas"),  # default is commas
    1: ("First Spot Value", "percent only"),
    2: ("Second Spot Value", "percent only")
}

optimal_dict = {
    1: ("Project (cost/worth)", "prj_list"),
    2: ("Budget", "commas"),
    3: ("Bond Yield List", "by_lst"),
    0: ("Return", "return")
}

menu_layout = {
    1: ("Value", values_dict),  # Present Value, Future Value, Cashflow
    2: ("Rate", rates_dict),   # Interest Rate, Effective Rate, Nominal Rate
    3: ("Loan", loans_dict),
    4: ("Bond", bonds_dict),
    5: ("Optimal", optimal_dict),
    0: "Complete"
}

ingredients_catalog = {}
for dictionary in [values_dict, rates_dict, bonds_dict, loans_dict, optimal_dict,
                   extra_format_storage]:
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

    def display_values(self, mode="Default"):
        if not self.valid:
            for item in self.missing_values:
                print(f"Missing data for '{item}'.")
            return
        bold_name = "\033[1m" + f"Calculating {self.title}" + "\033[0m"
        if mode == "Default":
            print(f'{bold_name:~^40}')
        for item in self.values:
            if item in ingredients_catalog and (item in self.requirements or mode != "Default"):
                if ingredients_catalog[item] in ("commas", "sp1", "sp2"):
                    print(f'{item:<20}: {format_numeric_value(self.values[item])}')
                elif ingredients_catalog[item] in ("percent", "percent only"):
                    print(f'{item:<20}: {self.values[item] * 100}%')
                elif ingredients_catalog[item] in ("cf", "sp_lst", "prj_list", "by_lst"):
                    print(f'{item:<20}: {self.values[item]}')
                else:
                    print(f'Failed to file-- {item}: {self.values[item]}')
            elif item not in self.requirements:
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


class PrincipalRemainingPV(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Principal Remaining in Present Value"
        self.title = "Remaining Principal in Present Value"
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
        return (self.pay / r) * (1 - 1 / (( 1 + r) ** n))


class PrincipalRemainingNV(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Principal Remaining in Nominal Value"
        self.title = "Remaining Principal in Nominal Value"
        self.requirements = ["Payments", "Periods", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.pay = self.values["Payments"]
            self.periods = self.values["Periods"]
            self.compound = self.values["Compound Method"]


    def calculate(self):
        super().calculate()
        compounding = compounding_methods[self.compound]
        return compounding * self.periods * self.pay

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
        D = MacaulayDuration(self.values).calculate()
        answer = (1 / (1 + self.y / self.m)) * D
        return str(answer) + f" or {answer:.2f} payments aka periods left."


class ChangeInBondPrice(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Change In Bond Price"
        self.title = "Change in Bond Price based on New Yield"
        self.requirements = ["Face Value", "Coupons", "Coupons per Period", "Yield", "New Yield",
                             "Periods"]
        self.valid = self.validate_values()
        if self.valid:
            self.fv = self.values["Face Value"]
            self.coup = self.values["Coupons"]  # Called % Coupon Bonds or % Bond
            self.m = self.values["Coupons per Period"]
            self.y = self.values["Yield"]  # Yield or Bond Yielding %
            self.ny = self.values["New Yield"]
            self.periods = self.values["Periods"]

    def calculate(self):
        super().calculate()
        P = BondPrice(self.values).calculate()
        D_m = (1 / (1 + self.y / self.m)) * MacaulayDuration(self.values).calculate()
        answer = - P * D_m * (self.ny - self.y)
        return str(answer) + f" or ${format_numeric_value(answer)} was the amount changed so the" \
                             f" new Price is:\n${format_numeric_value(answer + P)}"


class ForwardRate(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Forward Rate"
        self.title = "Forward Rate aka the Predicted Rate for the Second Year"
        self.requirements = ["First Spot Year", "First Spot Value", "Second Spot Year",
                             "Second Spot Value", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.i = self.values["First Spot Year"]
            self.s_i = self.values["First Spot Value"]
            self.j = self.values["Second Spot Year"]
            self.s_j = self.values["Second Spot Value"]
            self.compound = self.values["Compound Method"]

    def calculate(self):
        super().calculate()
        if compounding_methods[self.compound] != "Continuous":
            m = compounding_methods[self.compound]
            fract = ((1 + self.s_j / m) ** self.j / (1 + self.s_i / m) ** self.i)
            answer = m * fract ** (1 / (self.j - self.i)) - m
        else:
            answer = (self.s_j * self.j - self.s_i * self.i) / (self.j - self.i)
        return f"of based on years {self.i}, for year {self.j} it is {answer * 100}%"


class FirstSpotRate(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "First Spot Rate"
        self.title = "Spot Rate aka Theoretical Yield for a Zero-Coup Bond for Second Year"
        self.requirements = ["First Spot Year", "Forward Rate", "Second Spot Year",
                             "Second Spot Value", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.i = self.values["First Spot Year"]
            self.fr = self.values["Forward Rate"]
            self.j = self.values["Second Spot Year"]
            self.s_j = self.values["Second Spot Value"]
            self.compound = self.values["Compound Method"]

    def calculate(self):
        super().calculate()
        if compounding_methods[self.compound] != "Continuous":
            m = compounding_methods[self.compound]
            fract_1 = (1 + self.s_j / m) ** self.j
            fract_2 = (1 + self.fr / m) ** (self.j - self.i)
            answer = ((fract_1 / fract_2) ** (-self.i) - 1) * m
        else:
            answer = -(self.fr * (self.j - self.i) - self.s_j * self.j) / self.i
        return f"for year {self.j} is {answer} or {answer * 100:.2f}%"


class SecondSpotRate(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Second Spot Rate"
        self.title = "Forward Rate aka the Predicted Rate for the Second Year"
        self.requirements = ["First Spot Year", "First Spot Value", "Second Spot Year",
                             "Forward Rate", "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.i = self.values["First Spot Year"]
            self.s_i = self.values["First Spot Value"]
            self.j = self.values["Second Spot Year"]
            self.fr = self.values["Forward Rate"]
            self.compound = self.values["Compound Method"]

    def calculate(self):
        super().calculate()
        if compounding_methods[self.compound] != "Continuous":
            m = compounding_methods[self.compound]
            fract_1 = (1 + self.s_i / m) ** (self.i/self.j)
            fract_2 = (1 + self.fr / m) ** ((self.j - self.i) / self.j)
            answer = (fract_1 * fract_2 - 1) * m
        else:
            answer = (self.fr * (self.j - self.i) + self.s_i * self.i) / self.j
        return f"for year {self.i} is {answer} or {answer * 100:.2f}%"


class QuasiModifiedDurationBond(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Quasi-Modified Duration from Bond"
        self.title = "Quasi-Modified Duration aka Sensitivity"
        self.requirements = ["Spot Rate List", "Face Value", "Coupons",
                             "Coupons per Period", "Compound Method", "Periods"]
        self.valid = self.validate_values()
        if self.valid:
            self.y_list = self.values["Spot Rate List"]
            self.fv = self.values["Face Value"]
            self.coup = self.values["Coupons"]
            self.compound = self.values["Compound Method"]
            self.periods = self.values["Periods"]

    def calculate(self):
        super().calculate()
        m = compounding_methods[self.compound]
        n = m * self.periods
        coup = self.coup / m
        entry_PV = {"Periods": 0, "Compound Method": self.compound}
        P_list = []
        D_list = []
        i = 1
        for y in self.y_list:
            if i > self.periods:
                break
            entry_PV["Periods"] = i
            entry_PV["Interest Rate"] = y
            if i == self.periods:
                entry_PV["Future Value"] = self.coup + self.fv
            else:
                entry_PV["Future Value"] = self.coup
            P_list.append(PresentValue(entry_PV).calculate())
            for j in range(1, m + 1):
                if i == self.periods and j == m:  # last iteration
                    coup = coup + self.fv
                k = (i - 1) * m + j
                D_list.append(coup * (k / m) * (1 + y / m) ** (-(k + 1)))
            i += 1
        return sum(D_list) / sum(P_list)


class ImmunizePortfolio(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Immunize Portfolio"
        self.title = "Immunization for Portfolio aka Minimize Impact from Change of Yield"
        self.requirements = ["Spot Rate List", "Face Value #1", "Coupons #1",
                             "Coupons per Period #1", "Periods #1", "Face Value #2", "Coupons #2",
                             "Coupons per Period #2", "Periods #2", "Obligations List",
                             "Compound Method"]
        self.valid = self.validate_values()
        if self.valid:
            self.y_list = self.values["Spot Rate List"]
            self.fv_1 = self.values["Face Value #1"]
            self.coup_1 = self.values["Coupons #1"]
            self.m_1 = self.values["Coupons per Period #1"]
            self.p_1 = self.values["Periods #1"]
            self.fv_2 = self.values["Face Value #2"]
            self.coup_2 = self.values["Coupons #2"]
            self.m_2 = self.values["Coupons per Period #2"]
            self.p_2 = self.values["Periods #2"]
            self.obl_list = self.values["Obligations List"]
            self.compound = self.values["Compound Method"]
            self.cm1 = self.values["Compound Method"]  # Can be Changed Manually
            self.cm2 = self.values["Compound Method"]  # Can be Changed Manually

    def calculate(self):
        super().calculate()
        def FindPresentValue(fv, coup, periods, compound, y_list):
            entry_P = {"Future Value": coup, "Compound Method": compound}
            P = []
            for i in range(1, periods + 1):
                entry_P["Periods"] = i
                if i == periods:
                    entry_P["Future Value"] = coup + fv
                entry_P["Interest Rate"] = y_list[i - 1]
                P.append(PresentValue(entry_P).calculate())
            return sum(P)
        def FindQuasiDuration(y_list, fv_1, coup_1, m_1, p_1, compound):
            entry_P = {"Spot Rate List": y_list, "Face Value": fv_1, "Coupons": coup_1,
                       "Coupons per Period": m_1, "Periods": p_1, "Compound Method":compound}
            return QuasiModifiedDurationBond(entry_P).calculate()
        m = compounding_methods[self.compound]
        P1 = FindPresentValue(self.fv_1, self.coup_1, self.p_1, self.cm1, self.y_list)
        P2 = FindPresentValue(self.fv_2, self.coup_2, self.p_2, self.cm2, self.y_list) # * 2.048960
        D_1 = FindQuasiDuration(self.y_list, self.fv_1, self.coup_1, self.m_1, self.p_1, self.cm1)
        D_2 = FindQuasiDuration(self.y_list, self.fv_2, self.coup_2, self.m_2, self.p_2, self.cm2)
        PV_list = []
        for i in range(len(self.obl_list)):
            PV_list.append(PresentValue({"Future Value": self.obl_list[i], "Interest Rate":
                self.y_list[i], "Periods": i + 1, "Compound Method": self.compound}).calculate())
        PV_ob  = sum(PV_list)
        Obl_list = []
        for i in range(len(self.obl_list)):
            for j in range(1, m + 1):
                k = i * m + j
                Obl_list.append(self.obl_list[i] * (k / m) * (1 + self.y_list[i] / m) ** (-(k + 1)))
        D_obl = sum(Obl_list) / PV_ob
        A = np.array([[P1, P2], [P1 * D_1, P2 * D_2]])
        B = np.array([PV_ob, PV_ob * D_obl])
        return np.linalg.solve(A, B)


class OptimalProject(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Optimal Projects"
        self.title = "Optimal number of Projects to Do"
        self.requirements = ["Project (cost/worth)", "Budget"]
        self.valid = self.validate_values()
        if self.valid:
            self.costs_tup = self.values["Project (cost/worth)"][0]
            self.worth_tup = self.values["Project (cost/worth)"][1]
            self.max = self.values["Budget"]

    def calculate(self):
        super().calculate()
        prob = LpProblem("Maximize_Value", LpMaximize)
        n = len(self.costs_tup)
        x = [LpVariable(f"x{i}", cat = "Binary") for i in range(n)]
        prob += lpSum(self.worth_tup[i] * x[i] for i in range(n)), "Total_Value"
        prob += lpSum(self.costs_tup[i] * x[i] for i in range(n)) <= self.max, "Budget_Constraint"
        prob.solve()
        selected_projects = [i + 1 for i in range(n) if x[i].varValue == 1]
        total_value = sum(self.worth_tup[i] for i in selected_projects)
        return f"/ are {selected_projects} with a max value of {total_value}"


class OptimizeParBonds(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Optimize Par-Bonds"
        self.title = "Optimize Par-Bonds against Obligations"
        self.requirements = ["Obligations List", "Periods", "Bond Yield List", "Face Value"]
        self.valid = self.validate_values()
        if self.valid:
            self.obl_list = self.values["Obligations List"]
            self.bond_y_list = self.values["Bond Yield List"]
            self.fv = self.values["Face Value"]
            self.periods = self.values["Periods"]

    def calculate(self):
        super().calculate()
        c = np.full(self.periods, self.fv)
        A = np.zeros((self.periods, self.periods))
        for i in range(self.periods):
            for j in range(i, self.periods):
                if i == j:
                    A[i, j] = self.fv + self.bond_y_list[j] * self.fv  # redemption value + coupon payment
                else:
                    A[i, j] = self.bond_y_list[j] * self.fv # coupon payment
        b = np.array(self.obl_list)
        result = linprog(c, A_ub = -A, b_ub = -b, method = "highs")
        answer = []
        for i, x in enumerate(result.x, 1):
            answer.append(f"Bond {i} ({self.bond_y_list[i - 1]}% annual coupon): {x:.2f} units")
        return '\n'.join(answer)

calculation_key = {
    "Future Value": FutureValue,
    "Present Value": PresentValue,
    "Cashflow": CashflowValue,
    "Internal Rate": InternalRate,
    "Nominal Rate": NominalRate,
    "Payments for Loan": PaymentLoan,
    "Principal Remaining in Present Value": PrincipalRemainingPV,
    "Principal Remaining in Nominal Value": PrincipalRemainingNV,
    "Perpetual Value": PerpetualValue,
    "Bond Price": BondPrice,   # Slightly off by .3%                    P and lamda should be switchable
    "Macaulay Duration": MacaulayDuration,   # Slightly off by 1%
    "Modified Duration": ModifiedDuration,
    "Yield To Maturity": YieldToMaturity,
    "Forward Rate": ForwardRate,
    "First Spot Rate": FirstSpotRate,
    "Second Spot Rate": SecondSpotRate,
    "Change In Bond Price": ChangeInBondPrice,
    "Quasi-Modified Duration from Bond": QuasiModifiedDurationBond,
    "Optimal Project": OptimalProject,
    "Optimize Par-Bonds": OptimizeParBonds,
    "Immunize Portfolio": ImmunizePortfolio
}

# create a discount factor
# error in 34:40 lec 6
# be able to enter a list of spot rates to find expected for next year (f1,2  f1,3  f1,4 )
# how to do payments given difference interest
# change in price, change for all relevant possibilities
# check normal duration calculation
# create coupon %
# allow it to be added with face value after assumption of FV 100

if __name__ == "__main__":
    data = {
        "Budget": 500.0,
        "Project (cost/worth)": [[100.0, 20.0, 150.0, 50.0, 50.0, 150.0, 150.0],
                                 [300.0, 50.0, 350.0, 110.0, 100.0, 250.0, 200.0]]
    }
    print(OptimalProject(data).calculate())



    data = {
        "Spot Rate List": [.0767, .0827, .0881, .0931, .0975, .1016, .1052, .1085, .1115, .1142,
                           .1167, .1189],
        "Face Value #1": 100,
        "Coupons #1": 6,
        "Coupons per Period #1": 1,
        "Periods #1": 12,
        "Face Value #2": 100,
        "Coupons #2": 10,
        "Coupons per Period #2": 1,
        "Periods #2": 5,
        "Compound Method": "Annual",
        "Obligations List": [100, 200, 300, 400, 500, 600, 700, 800]
    }
    print(ImmunizePortfolio(data).calculate())



    data = {
        "Obligations List": [150, 250, 400, 550, 700, 850, 1000, 1200],
        "Bond Yield List": [.005, .01, .015, .02, .025, .03, .035, .04],
        "Periods": 8,
        "Face Value": 100
    }
    print(OptimizeParBonds(data).calculate())