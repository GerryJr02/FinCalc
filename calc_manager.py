

import copy


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
    2: ("Nominal Principal", "commas"),
    3: ("Payments", "commas"),
    4: ("Perpetual Value", "commas"),
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
    9: ("Change in Bond Price", "commas"),
    10: ("Change in Yield", "percent"),
    11: ("Modified Duration", "commas"),
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
        self._original_values_ = values
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


