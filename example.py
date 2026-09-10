"""
Internal Credit Tracker
Level 2 DTC programming exemplar

Purpose:
    Help a student record NCEA internals, update results, and see progress
    towards a credit target.

Advanced techniques demonstrated:
    - A list of dictionaries stores and modifies multidimensional data.
    - Functions use parameters and return values.
    - Non-basic string manipulation supports searching and tidy display.
    - The json and pathlib libraries save and reload data.
"""


#this is importing the json database module
import json
from pathlib import Path


DATA_FILE = Path("internal_credits.json")
VALID_RESULTS = (
    "Not Started",
    "In Progress",
    "Submitted",
    "Achieved",
    "Merit",
    "Excellence",
)
PASSING_RESULTS = {"Achieved", "Merit", "Excellence"}


def normalise_standard_number(raw_number):
    """Return a standard number without spaces and in upper case."""
    return raw_number.strip().upper().replace(" ", "")


def clean_title(raw_title):
    """Remove extra spaces and return a readable title."""
    return " ".join(raw_title.strip().split())


def get_non_empty_text(prompt):
    """Repeatedly request text until the user enters at least one character."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Please enter some text. This field cannot be blank.")


def get_integer(prompt, minimum, maximum=None):
    """
    Return a validated integer within the supplied range.

    The function handles unexpected text with try/except and checks relevant
    lower and upper boundaries before returning a value.
    """
    while True:
        raw_value = input(prompt).strip()
        try:
            number = int(raw_value)
        except ValueError:
            print("Please enter a whole number, such as 6.")
            continue

        if number < minimum:
            print(f"Please enter a number of at least {minimum}.")
        elif maximum is not None and number > maximum:
            print(f"Please enter a number no greater than {maximum}.")
        else:
            return number


def choose_from_menu(prompt, options):
    """Display a flexible numbered menu and return the selected option."""
    for index, option in enumerate(options, start=1):
        print(f"{index}. {option}")

    choice = get_integer(prompt, 1, len(options))
    return options[choice - 1]


def find_internal_index(internals, standard_number):
    """Return the list index of a matching standard, or -1 when not found."""
    wanted_number = normalise_standard_number(standard_number)
    for index, internal in enumerate(internals):
        if internal["standard_number"] == wanted_number:
            return index
    return -1


def calculate_summary(internals, target_credits):
    """
    Calculate progress values and return them in a dictionary.

    Derived values are calculated from the collection rather than being stored
    separately, which prevents totals becoming out of date.
    """
    total_available = sum(internal["credits"] for internal in internals)
    achieved_credits = sum(
        internal["credits"]
        for internal in internals
        if internal["result"] in PASSING_RESULTS
    )
    remaining_credits = max(target_credits - achieved_credits, 0)
    progress_percent = (
        min((achieved_credits / target_credits) * 100, 100)
        if target_credits > 0
        else 0
    )

    return {
        "total_available": total_available,
        "achieved_credits": achieved_credits,
        "remaining_credits": remaining_credits,
        "progress_percent": progress_percent,
    }


def add_internal(internals):
    """Collect validated details and add one unique internal to the list."""
    print("\nADD AN INTERNAL")
    standard_number = normalise_standard_number(
        get_non_empty_text("Standard number (for example AS91896): ")
    )

    if find_internal_index(internals, standard_number) != -1:
        print("That standard is already in the tracker, so it was not added.")
        return False

    title = clean_title(get_non_empty_text("Internal title: "))
    credits = get_integer("Credits (1-20): ", 1, 20)
    result = choose_from_menu("Choose the current result: ", VALID_RESULTS)

    # Each dictionary is one record inside the main list collection.
    internals.append(
        {
            "standard_number": standard_number,
            "title": title,
            "credits": credits,
            "result": result,
        }
    )
    print(f"{standard_number} was added.")
    return True


def display_internals(internals):
    """Display all records in aligned columns without changing the data."""
    print("\nMY INTERNALS")
    if not internals:
        print("No internals have been added yet.")
        return

    print(f"{'Standard':<12}{'Cr':>4}  {'Result':<14}Title")
    print("-" * 68)
    for internal in internals:
        print(
            f"{internal['standard_number']:<12}"
            f"{internal['credits']:>4}  "
            f"{internal['result']:<14}"
            f"{internal['title']}"
        )


def update_result(internals):
    """Find a standard and modify its result after validation."""
    print("\nUPDATE A RESULT")
    standard_number = get_non_empty_text("Standard number to update: ")
    index = find_internal_index(internals, standard_number)

    if index == -1:
        print("That standard is not in the tracker.")
        return False

    old_result = internals[index]["result"]
    new_result = choose_from_menu("Choose the new result: ", VALID_RESULTS)
    internals[index]["result"] = new_result
    print(f"Result changed from {old_result} to {new_result}.")
    return True


def remove_internal(internals):
    """Remove a matching record only after the user confirms the action."""
    print("\nREMOVE AN INTERNAL")
    standard_number = get_non_empty_text("Standard number to remove: ")
    index = find_internal_index(internals, standard_number)

    if index == -1:
        print("That standard is not in the tracker.")
        return False

    internal = internals[index]
    confirmation = input(
        f"Remove {internal['standard_number']} - {internal['title']}? (y/n): "
    ).strip().lower()

    if confirmation == "y":
        removed = internals.pop(index)
        print(f"{removed['standard_number']} was removed.")
        return True

    print("Removal cancelled.")
    return False


def search_internals(internals):
    """
    Search across standard numbers and titles using normalised strings.

    Joining fields and converting them to lower case allows a partial,
    case-insensitive search such as 'program' or '91896'.
    """
    print("\nSEARCH INTERNALS")
    search_term = get_non_empty_text("Search word or standard number: ").lower()
    matches = []

    for internal in internals:
        searchable_text = (
            f"{internal['standard_number']} {internal['title']}"
        ).lower()
        if search_term in searchable_text:
            matches.append(internal)

    if matches:
        display_internals(matches)
    else:
        print("No matching internals were found.")
    return matches


def display_summary(internals, target_credits):
    """Display calculated credit progress and a message suited to the result."""
    summary = calculate_summary(internals, target_credits)
    print("\nCREDIT SUMMARY")
    print(f"Credits available in tracker: {summary['total_available']}")
    print(f"Credits achieved:             {summary['achieved_credits']}")
    print(f"Target credits:               {target_credits}")
    print(f"Credits still needed:         {summary['remaining_credits']}")
    print(f"Progress towards target:      {summary['progress_percent']:.1f}%")

    if summary["achieved_credits"] >= target_credits:
        print("Ka pai! You have reached your target.")
    elif summary["achieved_credits"] == 0:
        print("No achieved credits are recorded yet. Keep working towards the target.")
    else:
        print("You are making progress. Keep going.")


def validate_loaded_data(data):
    """
    Return only records with the required types and sensible field values.

    This prevents incomplete or edited JSON data from crashing later parts of
    the program.
    """
    if not isinstance(data, list):
        return []

    valid_records = []
    for item in data:
        if not isinstance(item, dict):
            continue

        required_keys = {"standard_number", "title", "credits", "result"}
        if not required_keys.issubset(item):
            continue
        if not isinstance(item["standard_number"], str):
            continue
        if not isinstance(item["title"], str):
            continue
        if not isinstance(item["credits"], int) or not 1 <= item["credits"] <= 20:
            continue
        if item["result"] not in VALID_RESULTS:
            continue

        valid_records.append(
            {
                "standard_number": normalise_standard_number(
                    item["standard_number"]
                ),
                "title": clean_title(item["title"]),
                "credits": item["credits"],
                "result": item["result"],
            }
        )
    return valid_records


def load_internals(file_path):
    """Load saved data, returning starter data if no save file exists."""
    if not file_path.exists():
        return [
            {
                "standard_number": "AS91896",
                "title": "Use advanced programming techniques",
                "credits": 6,
                "result": "In Progress",
            },
            {
                "standard_number": "AS91897",
                "title": "Use advanced processes",
                "credits": 6,
                "result": "In Progress",
            },
        ]

    try:
        with file_path.open("r", encoding="utf-8") as file:
            loaded_data = json.load(file)
    except (OSError, json.JSONDecodeError):
        print("The save file could not be read. Starting with an empty tracker.")
        return []

    valid_data = validate_loaded_data(loaded_data)
    if len(valid_data) < len(loaded_data):
        print("Warning: one or more invalid saved records were ignored.")
    return valid_data


def save_internals(internals, file_path):
    """Save all records as readable JSON and report whether saving succeeded."""
    try:
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(internals, file, indent=4, ensure_ascii=False)
    except OSError:
        print("The data could not be saved. Check the folder permissions.")
        return False

    print("Progress saved successfully.")
    return True


def main():
    """Run the menu until the user chooses to save and exit."""
    internals = load_internals(DATA_FILE)
    print("INTERNAL CREDIT TRACKER")
    print("Track your standards and progress towards an NCEA credit target.")
    target_credits = get_integer("Enter your credit target (1-120): ", 1, 120)

    menu_options = (
        "View all internals",
        "Add an internal",
        "Update a result",
        "Remove an internal",
        "Search internals",
        "View credit summary",
        "Save and exit",
    )

    while True:
        print("\nMAIN MENU")
        choice = choose_from_menu("Choose an option: ", menu_options)

        if choice == "View all internals":
            display_internals(internals)
        elif choice == "Add an internal":
            add_internal(internals)
        elif choice == "Update a result":
            update_result(internals)
        elif choice == "Remove an internal":
            remove_internal(internals)
        elif choice == "Search internals":
            search_internals(internals)
        elif choice == "View credit summary":
            display_summary(internals, target_credits)
        else:
            save_internals(internals, DATA_FILE)
            print("Goodbye.")
            break


if __name__ == "__main__":
    main()