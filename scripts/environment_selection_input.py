from typing import List, Optional


def ask_question(options: List[str]) -> Optional[str]:
    print("Which environment do you want to refresh connections for?")
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")

    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")


options_list = ["dev", "prod", "exit"]
selected_option = ask_question(options_list)

print(f"You selected: {selected_option}")
