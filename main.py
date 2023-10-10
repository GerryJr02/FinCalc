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
            chosen_calc = self.receive_info()
            if chosen_calc:
                calc = calculation_class_key[chosen_calc](self.value_dict)
                if all(key in self.value_dict for key in possible_calculation[chosen_calc]):
                    print('\n' * 40)
                    calc.display_values()
                    complete = input('Would you like to calculate? (Y/N): ')
                    if complete.strip().upper() == 'Y':
                        answer = calc.calculate()
                        print("\n" * 40)
                        calc.display_values()
                        print(f"\nThe {chosen_calc} is {answer}")
                else:
                    print("Cannot Complete Calculation, these items are currently missing:")
                    for item in calc.missing_values:
                        print(f"{item} Missing")

                next_calc = input('\nWould you like to continue? (Y/N): ')


    def receive_info(self):
        option = input('Selecting Option: ')
        print()
        if option == '0':
            valid_calculations = []
            for key, calc in calculation_class_key.items():
                if calc(self.value_dict).valid:
                    valid_calculations.append(key)
            if valid_calculations:
                i = 1
                print('Based on Information, I can Calculate the following:')
                for item in valid_calculations:
                    print(f'{i}: {item}')
                    i += 1
                print(f'0: Return')
                calc_selected = int(input('\nWhich calculation would you like?: '))
                if calc_selected:
                    return valid_calculations[calc_selected - 1]
                else:
                    return False
            else:
                closest_calculations = []
                max_similarity = -1
                for key, calc in calculation_class_key.items():
                    info_needed = len(possible_calculation[key])
                    missing = len(calc(self.value_dict).missing_values)
                    similarity =  (info_needed - missing) / info_needed

                    if similarity > max_similarity:
                        max_similarity = similarity
                        closest_calculations = [(key, calc(self.value_dict).missing_values)]
                    elif similarity == max_similarity:
                        closest_calculations.append((key, calc(self.value_dict).missing_values))
                print('\nCannot Calculate, Information is Missing')
                print("\nHere are my suggestion(s):")
                for key, items in closest_calculations:
                    key_str = f"Key: {key}"
                    print(f'{key_str:<20} | Missing: {items}')
                input("Press Enter to Continue: ")

        elif option == '1':
            self.value_dict["Present Value"] = \
                float(input('Enter Present Value (commas allowed): ').strip().replace(",", ""))

        elif option == '2':
            self.value_dict["Rate"] = \
                float(input('Enter Interest Rate (Percent): ').strip().replace(",", "")) / 100

        elif option == '3':
            self.value_dict["Periods"] = \
                float(input('Enter How long is the Period: ').strip().replace(",", ""))

        elif option == '4':
            ################################################################################################
            cf = [-800000.0, 24000.0, 24000.0, 24000.0, 24000.0, 24000.0, 24000.0, 24000.0, 24000.0, 24000.0, 1024000.0] # Manually add Cash Flow here
            if cf:
                print(f'Entering: {cf}')
                self.value_dict["Cashflow"] = cf
                self.value_dict["Start Year"] = float(input("Enter Start Year: (Typically 0): "))
                return
            ################################################################################################
            cf_value = input('Enter Cashflow (enter "Q" when finished): ').strip().replace(",", "")
            while cf_value.strip().upper() != 'Q':
                cf.append(float(cf_value))
                cf_value = input('Enter Cashflow (enter "Q" when finished): ')
            self.value_dict["Cashflow"] = cf
            self.value_dict["Start Year"] = float(input("Enter Start Year: (Typically 0): "))

        elif option == '5':
            self.value_dict["Future Value"] = \
                float(input('Enter Future Value (commas allowed): ').strip().replace(",", ""))

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
                self.value_dict["Custom"] = \
                    int(input('Enter the compounds per Period: ').strip().replace(",", ""))
            else:
                print('Invalid option. Please select a valid option.')
                print("\n" * 5)
                return "Value"
        else:
            print('Invalid option. Please select a valid option.')

        print("\n" * 30)
        return False


    def menu(self, mode="Default"):
        def format_numeric_value(value):
            try:
                return f"{float(value):,}" if value != "" else ""
            except Exception:
                return value

        if mode == "Default":
            print(f'1: Present Value    '
                  f'{format_numeric_value(self.value_dict.get("Present Value", ""))}')
            print(f'2: Interest Rate    '
                  f'{self.value_dict.get("Rate", "") * 100}%')
            print(f'3: Periods for rate '
                  f'{format_numeric_value(self.value_dict.get("Periods", ""))}')
            print(f'4: Enter Cashflow   '
                  f'{format_numeric_value(self.value_dict.get("Cashflow", ""))}')
            print(f'5: Future Value     '
                  f'{format_numeric_value(self.value_dict.get("Future Value", ""))}')
            print(f'6: Compound Method  '
                  f'{format_numeric_value(self.value_dict.get("Compound Method", ""))}')
            print('0: Complete')


if __name__ == '__main__':
    x = InterestCalculator()
    x.get_info()



