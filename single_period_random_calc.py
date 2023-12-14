

from calc_manager import OutlineCalculation, compounding_methods, format_numeric_value


class TotalReturn(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Total Return"  # include title
        self.requirements = ["Amount Received", "Amount Invested"]
        self.valid = self.validate_values()
        if self.valid:
            self.AR = self.values["Amount Received"]
            self.AI = self.values["Amount Invested"]

    def calculate(self):
        super().calculate()
        return self.AR / self.AI


class RateOfReturn(OutlineCalculation):
    def __init__(self, values: dict):
        super().__init__(values)
        self.calc = "Total Return"  # include title
        self.requirements = ["Amount Received", "Amount Invested"]
        self.valid = self.validate_values()
        if self.valid:
            self.AR = self.values["Amount Received"]
            self.AI = self.values["Amount Invested"]

    def calculate(self):
        super().calculate()
        return (self.AR - self.AI) / self.AI


single_rand_key = {
    "Total Return": TotalReturn,
    "Rate of Return": RateOfReturn
}
