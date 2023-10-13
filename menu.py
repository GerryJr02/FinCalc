from Computation import *


values_dict = {
    1: ("Present Value", "commas"),  #  Commas Allowed
    2: ("Future Value", "commas"),
    3: ("Cashflow", "cf"),           #  Cashflow Entry is Unique
    0: ("Return", "return")
}


rates_dict = {
    1: ("Interest Rate", "percent", "Rate"),   #  Percentage Entry,
    2: ("Effective Rate", "percent"),
    3: ("Nominal Rate", "percent"),
    4: ("Periods", "commas"),
    0: ("Return", "return")
}


menu_layout = {
    1: ("Value", values_dict),  # Present Value, Future Value, Cashflow
    2: ("Rate", rates_dict),   # Interest Rate, Effective Rate, Nominal Rate
    3: ("Bond", "Not Ready"),
    0: "Complete"
}

sub_dicts = [values_dict, rates_dict]


def format_val(value):
    try:
        return f"{float(value):,}" if value != "" else ""
    except Exception:
        return value

def display_current_info(current_dict):
    if current_dict:
        bold_name = "\033[1m" + "Current Information" + "\033[0m"
        print(f'{bold_name:~^50}')
        i = 1

        for key, value in current_dict.items():
            print(f'{i}: {key:<20}{format_val(value)}')
            i += 1
        print()


def select_entry():
    for i in range(1, len(menu_layout)):
        print(f'{i}: {menu_layout[i][0]}')  # Display Main Menu Options
    print("0: Complete")
    option = int(input('Selecting Option: ').strip())
    if option == 0:
        return "complete", "complete"
    print('\n' * 40)

    sub_menu = menu_layout[option][1]
    for i in range(1, len(sub_menu)):
        print(f'{i}: {sub_menu[i][0]}')  # Display Main Menu Options
    selection = int(input(f'Selecting {menu_layout[option][0]} Option: ').strip())
    print()
    return sub_menu[selection]


def enter_value(value_dict) -> (None, str):
    print('\n' * 40)
    display_current_info(value_dict)
    entry = select_entry()
    entry_type = entry[1]

    if entry_type == "commas":
        disc = "(commas allowed)"  # Disclaimer for Entry
        value_dict[entry[0]] = float(input(f'Enter {entry[0]} {disc}: ').strip().replace(",", ""))
    elif entry_type == "percent":
        disc = "(as a Percent)"
        if len(entry) > 2:
            if entry[2] == "Rate":
                value_dict[entry[2]] = float(input(f'Enter {entry[0]} {disc}: ').strip()) / 100
        else:
            value_dict[entry[0]] = float(input(f'Enter {entry[0]} {disc}: ').strip()) / 100
        value_dict['Compound Method'] = enter_compound_method()
    elif entry_type == "cf":
        value_dict[entry[0]] = enter_cashflow()
        disc = "(typically 0)"
        value_dict["Start Year"] = float(input(f'Enter Start Year {disc}: ').strip())


    elif entry_type == "complete":
        return complete_calculation_entry(value_dict)
    elif entry_type == "return":
        return


def complete_calculation_entry(value_dict) -> (None, str):
    print('\n' * 40)
    valid_calculations = []
    for key, calc in calculation_key.items():
        if calc(value_dict).valid:
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
            return
    else:
        closest_calculations = []
        max_similarity = -1
        for key, calc in calculation_key.items():
            calc_obj = calc(value_dict)
            info_needed = len(calc_obj.requirements)
            missing = len(calc_obj.missing_values)
            similarity = (info_needed - missing) / info_needed

            if similarity > max_similarity:
                max_similarity = similarity
                closest_calculations = [(key, calc_obj.missing_values)]
            elif similarity == max_similarity:
                closest_calculations.append((key, calc_obj.missing_values))
        print('\nCannot Calculate, Information is Missing')
        print("\nHere are my suggestion(s):")
        for key, items in closest_calculations:
            key_str = f"Key: {key}"
            print(f'{key_str:<20} | Missing: {items}')
        input("\nPress Enter to Continue: ")


def enter_compound_method():
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
        return compound_options[int(compound.strip())]


def enter_cashflow():
    cashflow = []

    if not cashflow:
        i = 0
        entry = input(f"Enter Cashflow #{i}: ")
        while entry.upper() != 'Q':
            cashflow.append(float(entry))
            i += 1
            entry = input(f"Enter Cashflow (Q to quit) #{i}: ").strip()

    return cashflow














