from Computation import menu_layout, calculation_key, OutlineCalculation


def format_val(value):
    try:
        return f"{float(value):,}" if value != "" else ""
    except Exception:
        return value


def display_current_info(current_dict):
    if current_dict:
        bold_name = "\033[1m" + "Current Information" + "\033[0m"
        print(f'{bold_name:~^50}')
        OC = OutlineCalculation(current_dict)
        OC.valid = True
        OC.display_values("No Title")
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
    elif entry_type == "percent" or entry_type == "percent only":
        disc = "(as a Percent)"
        value_dict[entry[0]] = float(input(f'Enter {entry[0]} {disc}: ').strip()) / 100
        if entry_type == "percent":
            value_dict['Compound Method'] = enter_compound_method()
    elif entry_type == "cf":
        enter_list(value_dict, "Cashflow")
        disc = "(typically 0)"
        value_dict["Start Year"] = float(input(f'Enter Start Year {disc}: ').strip())
    elif entry_type == "comp":
        value_dict['Compound Method'] = enter_compound_method()
    elif entry_type in ["sp1", "sp2"]:
        enter_spot_rates(value_dict, entry_type)
    elif entry_type == "sp_lst":
        enter_list(value_dict, "Spot Rate List")
    elif entry_type == "prj_list":
        enter_list(value_dict, "Project (cost/worth)")
    elif entry_type == "by_lst":
        enter_list(value_dict, "Bond Yield List")
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

        x = input("\nPress Enter to Continue or \"0\" for more options: ")
        if x.strip() == "0":
            for key, calc in calculation_key.items():
                calc_obj = calc(value_dict)
                info_needed = len(calc_obj.requirements)
                missing = len(calc_obj.missing_values)
                similarity = (info_needed - missing) / info_needed
                if similarity > 0:
                    key_str = f"Key: {key}"
                    print(f'{key_str:<20} | Missing: {calc_obj.missing_values}')
            input("\nPress Enter to Continue")



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


def enter_spot_rates(value_dict, entry_type):
    if entry_type[-1] == "1":
        value_dict["First Spot Year"] = float(input(f'Enter Lower Spot Year (commas '
                                           f'allowed): ').strip().replace(",", ""))
        value = input(f'Enter Spot Value for position 1 (as a Percent): ')
        if value.strip() != "":
            value_dict["First Spot Value"] = float(value.strip()) / 100
    elif entry_type[-1] == "2":
        value_dict["Second Spot Year"] = float(input(f'Enter Lower Spot Year (commas '
                                           f'allowed): ').strip().replace(",", ""))
        value = input(f'Enter Spot Value for position 2 (as a Percent): ')
        if value.strip() != "":
            value_dict["Second Spot Value"] = float(value.strip()) / 100


def enter_list(value_dict, mode):
    disc = "(Q to quit)"
    percent = False
    optional = False
    enter_str = ""
    enter_str_opt = ""
    i = 1

    if mode == "Cashflow":
        i = 0
        enter_str = "Enter Cashflow"
    elif mode == "Spot Rate List":
        percent = False
        enter_str = "Enter Spot Rate"
    elif mode == "Project (cost/worth)":
        enter_str = "Enter Project Cost"
        optional = True
        enter_str_opt = "Enter Project Worth"
    elif mode == "Bond Yield List":
        enter_str = "Enter Bond Yield (Percent)"
        percent = True

    entry = input(f"{enter_str} #{i}: ").strip()
    output = []
    output_opt = []
    print("I got", entry)
    while entry.upper() != 'Q':
        print("I entered")
        if percent:
            output.append(float(entry) / 100)
        else:
            output.append(float(entry))
            print("added to list")
        if optional:
            entry_opt = input(f"{enter_str_opt} #{i}: ")
            output_opt.append(float(entry_opt))
        i += 1
        entry = input(f"{enter_str} {disc} #{i}: ").strip()

    if optional:
        value_dict[mode] = [output, output_opt]
    else:
        value_dict[mode] = output











