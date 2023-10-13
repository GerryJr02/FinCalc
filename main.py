# Discussion 1
from Computation import *
from menu import enter_value

class InterestCalculator:
    def __init__(self):
        self.value_dict = {}
        memory = []

    def run(self):
        next_calc = 'Y'
        while next_calc.strip().upper() != 'N' or next_calc.strip() != '0':
            try:
                chosen_calc = enter_value(self.value_dict)
            except Exception as e:
                print('Here\' your hint:', e)
                chosen_calc = ''

            if chosen_calc:  # Calculation Identified
                calc = calculation_key[chosen_calc](self.value_dict)  # find Calc Class
                if all(key in self.value_dict for key in calc.requirements):  # double check reqs
                    print('\n' * 40)
                    calc.display_values()
                    complete = input('Would you like to calculate? (Y/N): ')
                    if complete.strip().upper() == 'Y' or complete.strip() == '1':
                        answer = calc.calculate()
                        print("\n" * 40)
                        calc.display_values()
                        print(f"\nThe {chosen_calc} is {answer}")

                else:  # Should not be able to run
                    print("Cannot Complete Calculation, these items are currently missing:")
                    for item in calc.missing_values:
                        print(f"{item} Missing")

                next_calc = input('\nWould you like to continue? (Y/N): ')



if __name__ == '__main__':
    x = InterestCalculator()
    x.run()



