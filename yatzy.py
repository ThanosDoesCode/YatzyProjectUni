import random

# Kategorier i protokollet
CATEGORIES = [
    "Ettor", "Tvåor", "Treor", "Fyror", "Femmor", "Sexor",
    "Ett par", "Två par", "Tretal", "Fyrtal",
    "Liten stege", "Stor stege", "Kåk", "Chans", "Yatzy"
]

# Övre delen (för bonus)
UPPER_CATEGORIES = ["Ettor", "Tvåor", "Treor", "Fyror", "Femmor", "Sexor"]


# -----------------------------
# DICE FUNCTIONS
# -----------------------------

def roll_dice(dice, keep):
    """Reroll only dice positions where keep[i] is False."""
    i = 0
    while i < 5:
        if keep[i] == False:
            dice[i] = random.randint(1, 6)
        i += 1
    return dice


def format_dice(dice):
    """Return dice as a printable string."""
    return "[" + "] [".join(str(x) for x in dice) + "]"


def get_frequency_list(dice):
    """
    freq[value] = how many times the value appears.
    Index 0 is unused.
    """
    freq = [0, 0, 0, 0, 0, 0, 0]
    for value in dice:
        freq[value] += 1
    return freq


# -----------------------------
# SCORING FUNCTIONS (ONE RULE EACH)
# -----------------------------

def score_upper(freq, value):
    """Score for Ettor/Tvåor/.../Sexor."""
    return freq[value] * value


def score_one_pair(freq):
    """Highest pair."""
    value = 6
    while value >= 1:
        if freq[value] >= 2:
            return value * 2
        value -= 1
    return 0


def score_two_pairs(freq):
    """Two highest different pairs."""
    pair1 = 0
    pair2 = 0

    value = 6
    while value >= 1:
        if freq[value] >= 2:
            if pair1 == 0:
                pair1 = value
            elif pair2 == 0:
                pair2 = value
                break
        value -= 1

    if pair1 != 0 and pair2 != 0:
        return pair1 * 2 + pair2 * 2
    return 0


def score_three_of_a_kind(freq):
    """Highest three of a kind."""
    value = 6
    while value >= 1:
        if freq[value] >= 3:
            return value * 3
        value -= 1
    return 0


def score_four_of_a_kind(freq):
    """Highest four of a kind."""
    value = 6
    while value >= 1:
        if freq[value] >= 4:
            return value * 4
        value -= 1
    return 0


def score_small_straight(dice):
    """1-2-3-4-5."""
    if sorted(dice) == [1, 2, 3, 4, 5]:
        return 15
    return 0


def score_large_straight(dice):
    """2-3-4-5-6."""
    if sorted(dice) == [2, 3, 4, 5, 6]:
        return 20
    return 0


def score_full_house(freq, dice):
    """Kåk = one pair + one three of a kind."""
    has_two = False
    has_three = False

    value = 1
    while value <= 6:
        if freq[value] == 2:
            has_two = True
        elif freq[value] == 3:
            has_three = True
        value += 1

    if has_two and has_three:
        return sum(dice)
    return 0


def score_chance(dice):
    """Sum of all dice."""
    return sum(dice)


def score_yatzy(freq):
    """Five equal dice."""
    value = 1
    while value <= 6:
        if freq[value] == 5:
            return 50
        value += 1
    return 0


def get_score_options(dice):
    """Build all score suggestions for current dice."""
    freq = get_frequency_list(dice)
    options = {}

    options["Ettor"] = score_upper(freq, 1)
    options["Tvåor"] = score_upper(freq, 2)
    options["Treor"] = score_upper(freq, 3)
    options["Fyror"] = score_upper(freq, 4)
    options["Femmor"] = score_upper(freq, 5)
    options["Sexor"] = score_upper(freq, 6)

    options["Ett par"] = score_one_pair(freq)
    options["Två par"] = score_two_pairs(freq)
    options["Tretal"] = score_three_of_a_kind(freq)
    options["Fyrtal"] = score_four_of_a_kind(freq)
    options["Liten stege"] = score_small_straight(dice)
    options["Stor stege"] = score_large_straight(dice)
    options["Kåk"] = score_full_house(freq, dice)
    options["Chans"] = score_chance(dice)
    options["Yatzy"] = score_yatzy(freq)

    return options


# -----------------------------
# SCORECARD FUNCTIONS
# -----------------------------

def get_upper_sum(scorecard):
    """Sum only upper section categories that are filled."""
    total_sum = 0
    for category in UPPER_CATEGORIES:
        if scorecard[category] is not None:
            total_sum += scorecard[category]
    return total_sum


def get_bonus(scorecard):
    """Bonus is 50 if upper sum >= 63."""
    if get_upper_sum(scorecard) >= 63:
        return 50
    return 0


def get_total_score(scorecard):
    """Total score = all filled rows + bonus."""
    total_sum = 0
    for category in CATEGORIES:
        if scorecard[category] is not None:
            total_sum += scorecard[category]
    return total_sum + get_bonus(scorecard)


# -----------------------------
# INPUT FUNCTIONS
# -----------------------------

def read_int(prompt, min_value=None, max_value=None):
    """Read an integer with validation."""
    while True:
        try:
            value = int(input(prompt))
            if min_value is not None and value < min_value:
                print("För litet värde.")
                continue
            if max_value is not None and value > max_value:
                print("För stort värde.")
                continue
            return value
        except ValueError:
            print("Skriv ett heltal.")


def read_keep_mask():
    """
    Example input: '1 3 5' means keep die 1, 3, 5.
    Enter = keep none.
    """
    text = input("Spara vilka tärningar? (1-5, ex: 1 3 5 | Enter=inga): ").strip()
    keep = [False, False, False, False, False]

    if text == "":
        return keep

    parts = text.split()
    for part in parts:
        if part.isdigit():
            index = int(part)
            if 1 <= index <= 5:
                keep[index - 1] = True

    return keep


# -----------------------------
# PRINT / UI FUNCTIONS
# -----------------------------

def print_scorecard(scorecard):
    """Print one player's scorecard."""
    print("\nProtokoll:")
    for category in CATEGORIES:
        score = scorecard[category]
        if score is None:
            print(f"  {category:<12}: -")
        else:
            print(f"  {category:<12}: {score}")

    print(
        f"\nÖvre summa: {get_upper_sum(scorecard)}   "
        f"Bonus: {get_bonus(scorecard)}   "
        f"Total: {get_total_score(scorecard)}\n"
    )


def get_available_categories(scorecard):
    """Return categories that are still empty."""
    available = []
    for category in CATEGORIES:
        if scorecard[category] is None:
            available.append(category)
    return available


def choose_category_and_score(options, scorecard):
    """
    Show available rows and let player choose one.
    Player can enter 0 to strike, or the exact suggested score.
    """
    available = get_available_categories(scorecard)

    print("Valbara rader:")
    i = 1
    for category in available:
        print(f"{i:2d}. {category:<12} (förslag: {options[category]})")
        i += 1

    choice = read_int("Välj radnummer: ", 1, len(available))
    category = available[choice - 1]
    suggested_score = options[category]

    while True:
        score = read_int(
            f"Poäng för '{category}' (0=stryk, förslag {suggested_score}): ", 0, 50
        )
        if score == 0:
            return category, 0
        if score == suggested_score:
            return category, score
        print("Ogiltigt. Välj 0 (stryk) eller exakt förslaget.")


def build_protocol_text(players, scorecards):
    """Build a formatted text version of the full Yatzy protocol."""
    lines = []
    lines.append("YATZY – PROTOKOLL\n")

    for name in players:
        scorecard = scorecards[name]
        lines.append("Spelare: " + name)

        for category in CATEGORIES:
            score = scorecard[category]
            if score is None:
                lines.append(f"  {category:<12}: -")
            else:
                lines.append(f"  {category:<12}: {score}")

        lines.append(f"  Övre summa   : {get_upper_sum(scorecard)}")
        lines.append(f"  Bonus        : {get_bonus(scorecard)}")
        lines.append(f"  TOTAL        : {get_total_score(scorecard)}")
        lines.append("")

    return "\n".join(lines)


def save_protocol_to_file(players, scorecards, filename):
    """Save the full protocol to a text file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(build_protocol_text(players, scorecards))


def bot_best_keep_mask(dice):
    """Bot keeps the value that occurs most often; ties go to the higher value."""
    freq = get_frequency_list(dice)

    best_value = 1
    best_count = freq[1]

    value = 2
    while value <= 6:
        if freq[value] > best_count:
            best_count = freq[value]
            best_value = value
        elif freq[value] == best_count and value > best_value:
            best_value = value
        value += 1

    keep = [False, False, False, False, False]
    i = 0
    while i < 5:
        if dice[i] == best_value:
            keep[i] = True
        i += 1
    return keep


def bot_choose_category_and_score(options, scorecard):
    """Bot chooses the available category with the highest score."""
    available = get_available_categories(scorecard)

    best_cat = available[0]
    best_score = options[best_cat]

    i = 1
    while i < len(available):
        category = available[i]
        score = options[category]
        if score > best_score:
            best_score = score
            best_cat = category
        i += 1

    return best_cat, best_score


def execute_bot_turn(dice, keep, roll_count, scorecard):
    """
    Run a full bot turn (up to 3 rolls + register score).
    Returns updated dice, keep, roll_count, and the chosen category/score.
    """
    dice = list(dice)
    keep = list(keep)
    roll_count = 0

    while roll_count < 3:
        if roll_count == 0:
            keep = [False, False, False, False, False]
        else:
            keep = bot_best_keep_mask(dice)

        dice = roll_dice(dice, keep)
        roll_count += 1

    options = get_score_options(dice)
    category, score = bot_choose_category_and_score(options, scorecard)
    return dice, keep, roll_count, options, category, score


# -----------------------------
# MAIN GAME LOOP
# -----------------------------

def main():
    print("Välkommen till Yatzy (textläge)!")
    player_count = read_int("Hur många spelare? (1-6): ", 1, 6)

    # Read player names
    players = []
    i = 0
    while i < player_count:
        name = input(f"Namn för spelare {i+1}: ").strip()
        if name == "":
            name = "Spelare" + str(i + 1)
        players.append(name)
        i += 1

    # Create one scorecard dictionary per player
    scorecards = {}
    for name in players:
        scorecards[name] = {}
        for category in CATEGORIES:
            scorecards[name][category] = None

    # One round per category (15 rounds)
    round_number = 1
    while round_number <= len(CATEGORIES):
        print("\n" + "=" * 60)
        print(f"RUNDA {round_number}/{len(CATEGORIES)}")
        print("=" * 60)

        for name in players:
            print("\n" + "-" * 60)
            print(name + "s tur")

            print_scorecard(scorecards[name])

            # Start with empty dice
            dice = [0, 0, 0, 0, 0]

            # Roll 1 (all dice)
            dice = roll_dice(dice, [False, False, False, False, False])
            print("Kast 1:", format_dice(dice))

            # Roll 2
            keep = read_keep_mask()
            dice = roll_dice(dice, keep)
            print("Kast 2:", format_dice(dice))

            # Roll 3
            keep = read_keep_mask()
            dice = roll_dice(dice, keep)
            print("Kast 3:", format_dice(dice))

            # Show suggestions and store chosen score
            options = get_score_options(dice)
            category, score = choose_category_and_score(options, scorecards[name])
            scorecards[name][category] = score

            print("\nRegistrerat:", category, "=", score)
            print("Total nu:", get_total_score(scorecards[name]))

        round_number += 1

    # Final ranking
    print("\n" + "=" * 60)
    print("SPELET ÄR SLUT!")
    print("=" * 60)

    results = []
    for name in players:
        results.append([get_total_score(scorecards[name]), name])

    results.sort(reverse=True)  # Highest score first

    place = 1
    for row in results:
        print(f"{place}. {row[1]}: {row[0]} poäng")
        place += 1

    print("\nVinnare:", results[0][1])

    # Optional save
    answer = input("\nVill du spara protokollet som textfil? (j/n): ").strip().lower()
    if answer == "j":
        filename = input("Filnamn (t.ex. protokoll.txt): ").strip()
        if filename == "":
            filename = "protokoll.txt"
        save_protocol_to_file(players, scorecards, filename)
        print("Sparat i", filename)


if __name__ == "__main__":
    main()