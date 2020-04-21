import sqlite3
from tabulate import tabulate
from termcolor import colored

connection = sqlite3.connect("main.db")
cursor = connection.cursor()

carbs_goal = 250
protein_goal = 150
fat_goal = 60

def to_calories(carbs, protein, fat):
    return 4 * (carbs + protein) + 9 * fat

def print_progress_bar(label, amount, total):
    ratio = amount / total
    if ratio > 1:
        ratio = 1
    start = "  " + label + ":" + (10 - len(label)) * " "
    size = 20
    left_size = int(ratio * size)
    right_size = size - left_size
    progress_bar = colored("[" + "=" * left_size, "green")
    progress_bar += colored("=" * right_size + "]", "red")
    tally = "{0:4}".format(int(amount)) + " / " + "{0:4}".format(int(total))
    print(start + progress_bar + " " * 4 + tally)

def main():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS foods(
            id INTEGER PRIMARY KEY,
            name TEXT,
            is_per_100g INT,
            carbs REAL,
            protein REAL,
            fat REAL
        )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items(
            item INTEGER,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            amount_consumed REAL
        )""")
    connection.commit()

    print("[1] Add new item")
    print("[2] Today's diary")
    print("[3] Add food type")
    print("[4] List food types")

    select = input()

    if select == "1":
        print("Adding item to diary...")
        add_item()
    elif select == "2":
        print()
        show_diary()
    elif select == "3":
        print("Adding new food type to db...")
        add_food()
    elif select == "4":
        print()
        list_foods()

def add_item():
    print()
    list_foods()
    print()
    select = input("ID: ")
    amount_consumed = input("Amount: ")
    cursor.execute("""
        INSERT INTO items (item, amount_consumed)
        VALUES(?, ?)""",
        (select, amount_consumed))
    connection.commit()

def show_diary():
    food_types = fetch_foods()
    cursor.execute("""
        SELECT
            name, amount_consumed, is_per_100g,
            carbs, protein, fat, strftime('%H:%M', time)
        FROM items
        INNER JOIN foods ON items.item=foods.id
        WHERE time > date('now', '-1 days')
        ORDER BY time
    """)

    rows = []

    total_calories = 0
    total_carbs = 0
    total_protein = 0
    total_fat = 0
    for row in cursor.fetchall():
        name, amount, is_per_100g, carbs, protein, fat, time = row

        calories = to_calories(carbs, protein, fat)

        total_calories += calories
        total_carbs += carbs
        total_protein += protein
        total_fat += fat

        if is_per_100g:
            amount = "%s g" % amount
        else:
            amount = "%s units" % amount

        rows.append((name, amount, carbs, protein, fat, time))
    print(tabulate(rows, (
        "Name", "Amount", "Carbs", "Protein", "Fat", "Time")))
    print()
    calories_goal = to_calories(carbs_goal, protein_goal, fat_goal)
    print_progress_bar("Calories", total_calories, calories_goal)
    print_progress_bar("Carbs", total_carbs, carbs_goal)
    print_progress_bar("Protein", total_protein, protein_goal)
    print_progress_bar("Fat", total_fat, fat_goal)
    print()

def add_food():
    print()
    name = input("Name: ")
    is_per_100g = input("Per 100 grams? [Y/n]: ")
    if is_per_100g.lower() == "n":
        is_per_100g = 0
    else:
        is_per_100g = 1
    carbs = input("Carbs: ")
    protein = input("Protein: ")
    fat = input("Fat: ")
    print()
    print("Adding:")
    print("  name         =", name)
    print("  is_per_100g  =", is_per_100g)
    print("  carbs        =", carbs)
    print("  protein      =", protein)
    print("  fat          =", fat)
    input()
    cursor.execute("""
        INSERT INTO foods (name, is_per_100g, carbs, protein, fat)
        VALUES(?, ?, ?, ?, ?)""",
        (name, is_per_100g, carbs, protein, fat))
    connection.commit()

def fetch_foods():
    cursor.execute("SELECT * FROM foods")
    return cursor.fetchall()

def list_foods():
    print(tabulate(fetch_foods(),
        ("ID", "Name", "Per 100g", "Carbs", "Protein", "Fat")))

if __name__ == "__main__":
    main()

