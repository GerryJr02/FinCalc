# Discussion 1
from Computation import *

class InterestCalculator:
    def __init__(self):
        self.value_dict = {}
        memory = []

    def get_info(self):
        next_calc = 'Y'
        while next_calc.strip().upper() != 'N':
            self.menu()
            self.receive_info()
            for key, items in possible_calculation.items():
                if all(item in self.value_dict for item in items):
                    print(f"Would you like me to calculate {key} using the following values: ")
                    if self.menu(key):
                        value = self.perform_calculation(key)
                        print(f"\nThe {key} is {value}")
                        print(f'${value:,.2f}')
                        if key == 'Future Value':
                            if self.value_dict["Periods"] == 1:
                                print(f'The Effective Interest Rate is {(((value / self.value_dict["Present Value"]) - 1) * 100):,}%')
                        elif key == 'Present Value':
                            # print(f'The Effective Interest Rate is {(self.value_dict["Future Value"] / value * 100):,}%')
                            pass
                        elif key == "Cashflow":
                            internal_rate = input("Would you like to know the Internal Rate? (Y/N): ").strip().upper()
                            if internal_rate == 'Y':
                                cashflow = self.value_dict['Cashflow']
                                starting_point = self.value_dict['Start Year']
                                c = sp.symbols('c')
                                equation = sum(coeff * c ** (i + starting_point) for i, coeff in enumerate(cashflow))
                                roots = sp.solve(equation, c)
                                real_roots = [root.evalf() for root in roots if root.is_real]
                                for c in real_roots:
                                    print(f'c (roots) = {c}')
                                    print(f'r = {1/c - 1}')

                        next_calc = input('\nWould you like to continue? (Y/N): ')


    def receive_info(self):
        option = input('Selecting Option: ')
        print()
        if option == '0':
            print(self.value_dict)
        elif option == '1':
            self.value_dict["Present Value"] = float(input('Enter Present Value'
                                                           ' (commas allowed): ').strip().replace(",", ""))
            if 'Cashflow' in self.value_dict:
                del self.value_dict['Cashflow']
            if 'Future Value' in self.value_dict:
                del self.value_dict['Future Value']


        elif option == '2':
            self.value_dict["Rate"] = float(input('Enter Interest Rate (decimal): ').strip().replace(",", ""))

        elif option == '3':
            self.value_dict["Periods"] = float(input('Enter How long is '
                                                     'the Period: ').strip().replace(",", ""))

        elif option == '4':
            cf = []
            cf_value = input('Enter Cashflow (enter "Q" when finished): ').strip().replace(",", "")
            while cf_value.strip().upper() != 'Q':
                cf.append(float(cf_value))
                cf_value = input('Enter Cashflow (enter "Q" when finished): ')
            self.value_dict["Cashflow"] = cf
            self.value_dict["Start Year"] = float(input("Enter Start Year: (Typically 0): "))
            if 'Present Value' in self.value_dict:
                del self.value_dict['Present Value']
            if 'Future Value' in self.value_dict:
                del self.value_dict['Future Value']

        elif option == '5':
            self.value_dict["Future Value"] = float(input('Enter Future Value '
                                                          '(commas allowed): ').strip().replace(",", ""))
            if 'Present Value' in self.value_dict:
                del self.value_dict['Present Value']
            if 'Cashflow' in self.value_dict:
                del self.value_dict['Cashflow']

        elif option == '6':
            print('1: Annual')
            print('2: Semi-Annual')
            print('3: Quarterly')
            print('4: Monthly')
            print('5: Continuous')
            print('0: Custom')
            compound_options = ['Custom', 'Annual', 'Semi-Annual', 'Quarterly', 'Monthly',
                                'Continuous']
            compound = input("\nSelecting Compound Method: ")
            if compound.strip() in ['1', '2', '3', '4', '5']:
                self.value_dict["Compound Method"] = compound_options[int(compound.strip())]
            elif compound.strip() == 0:
                self.value_dict["Compound Method"] = 'Custom'
                self.value_dict["Custom"] = int(input('Enter the compounds per Period: ').strip().replace(",", ""))
            else:
                print('Invalid option. Please select a valid option.')
                print("\n" * 5)
                return
        else:
            print('Invalid option. Please select a valid option.')

        print("\n"*30)


    def menu(self, mode="Default"):
        def format_numeric_value(value):
            try:
                return f"{float(value):,}" if value != "" else ""
            except Exception:
                return value

        if mode == "Default":
            print(f'1: Present Value    {format_numeric_value(self.value_dict.get("Present Value", ""))}')
            print(f'2: Interest Rate    {self.value_dict.get("Rate", "") * 100}%')
            print(f'3: Periods for rate {format_numeric_value(self.value_dict.get("Periods", ""))}')
            print(f'4: Enter Cashflow   {format_numeric_value(self.value_dict.get("Cashflow", ""))}')
            print(f'5: Future Value     {format_numeric_value(self.value_dict.get("Future Value", ""))}')
            print(f'6: Compound Method  {format_numeric_value(self.value_dict.get("Compound Method", ""))}')
            print('0: Complete')

        if mode == "Future Value":
            print(f'Present Value: {format_numeric_value(self.value_dict.get("Present Value", ""))}')
            print(f'Interest Rate Percent:" {self.value_dict.get("Rate", "") * 100}%')
            print(f'Periods:" {format_numeric_value(self.value_dict.get("Periods", ""))}')
            print(f'Compound Method:" {format_numeric_value(self.value_dict.get("Compound Method", ""))}')
            confirm = input("Would you like to calc? (Y/N): ")
            if confirm.upper().strip() == "Y":
                return True
            else:
                return False

        elif mode == "Present Value":
            print(f'Future Value: {format_numeric_value(self.value_dict.get("Future Value", ""))}')
            print(f'Interest Rate Percent:" {self.value_dict.get("Rate", "") * 100}%')
            print(f'Periods:" {format_numeric_value(self.value_dict.get("Periods", ""))}')
            print(f'Compound Method:" {format_numeric_value(self.value_dict.get("Compound Method", ""))}')
            confirm = input("Would you like to calc? (Y/N): ")
            if confirm.upper().strip() == "Y":
                return True
            else:
                return False

        elif mode == "Cashflow":
            print(f'Cashflow: {self.value_dict["Cashflow"]}')
            print(f'Interest Rate Percent:" {self.value_dict.get("Rate", "") * 100}%')
            print(f'Start Year:" {(self.value_dict.get("Start Year", ""))}')
            print(
                f'Compound Method:" {format_numeric_value(self.value_dict.get("Compound Method", ""))}')
            confirm = input("Would you like to calc? (Y/N): ")
            if confirm.upper().strip() == "Y":
                return True
            else:
                return False


    def perform_calculation(self, calculation_type):
        required_items = possible_calculation.get(calculation_type, [])

        if not required_items:
            print("Invalid calculation type. Please select a valid calculation type.")
            return None

        entry_data = {}
        for item in required_items:
            if item in self.value_dict:
                entry_data[item] = self.value_dict[item]
            else:
                print(f"Missing data for '{item}' in value_dict.")
                return None

        if calculation_type == "Future Value":
            future_value = calculate_future_value(entry_data["Present Value"], entry_data["Rate"],
                                                  entry_data["Periods"],
                                                  entry_data["Compound Method"],
                                                  entry_data.get("Custom", None))
            return future_value
        elif calculation_type == "Present Value":
            present_value = calculate_present_value(entry_data["Future Value"], entry_data["Rate"],
                                                    entry_data["Periods"],
                                                    entry_data["Compound Method"],
                                                    entry_data.get("Custom", None))
            return present_value

        elif calculation_type == "Cashflow":
            present_accumulative = calculate_cashflow(entry_data["Cashflow"], entry_data["Rate"],
                                                      entry_data["Start Year"],
                                                      entry_data["Compound Method"],
                                                      entry_data.get("Custom", None))
            return present_accumulative
        else:
            print("Unsupported calculation type. Please wait for future development.")
            return None


if __name__ == '__main__':
    x = InterestCalculator()
    x.get_info()




