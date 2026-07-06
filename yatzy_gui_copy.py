"""
Streamlit UI for Yatzy.
All game logic lives in yatzy.py.
"""

import streamlit as st

from yatzy import (
    CATEGORIES,
    build_protocol_text,
    execute_bot_turn,
    get_available_categories,
    get_bonus,
    get_score_options,
    get_total_score,
    get_upper_sum,
    roll_dice,
)


def _dice_display(value):
    if value == 0:
        return "0"
    return str(value)


def _default_state():
    return {
        "screen": "start",
        "players": [],
        "scorecards": {},
        "is_bot": {},
        "current_player_index": 0,
        "round_number": 1,
        "roll_count": 0,
        "dice": [0, 0, 0, 0, 0],
        "keep": [False, False, False, False, False],
        "options": {},
        "selected_category": None,
        "score_input": "",
        "player_count": 2,
        "player_names": [f"Spelare{i + 1}" for i in range(6)],
        "player_bots": [False] * 6,
        "confirm_exit": False,
        "flash": None,
        "flash_type": "info",
        "results_text": "",
    }


def init_session_state():
    if "game" not in st.session_state:
        st.session_state.game = _default_state()


def _g():
    return st.session_state.game


def _set_flash(message, flash_type="info"):
    _g()["flash"] = message
    _g()["flash_type"] = flash_type


def _clear_flash():
    _g()["flash"] = None


def _show_flash():
    flash = _g()["flash"]
    if not flash:
        return
    flash_type = _g()["flash_type"]
    if flash_type == "success":
        st.success(flash)
    elif flash_type == "error":
        st.error(flash)
    elif flash_type == "warning":
        st.warning(flash)
    else:
        st.info(flash)
    _clear_flash()


def _current_player_name():
    return _g()["players"][_g()["current_player_index"]]


def _current_scorecard():
    return _g()["scorecards"][_current_player_name()]


def _is_current_player_bot():
    return _g()["is_bot"].get(_current_player_name(), False)


def _reset_turn_state():
    _g()["roll_count"] = 0
    _g()["dice"] = [0, 0, 0, 0, 0]
    _g()["keep"] = [False, False, False, False, False]
    _g()["options"] = {}
    _g()["selected_category"] = None
    _g()["score_input"] = ""


def _check_game_end():
    if _g()["round_number"] > len(CATEGORIES):
        _finish_game()
        return True
    return False


def _finish_game():
    results = []
    for name in _g()["players"]:
        results.append([get_total_score(_g()["scorecards"][name]), name])
    results.sort(reverse=True)

    lines = []
    place = 1
    for row in results:
        lines.append(f"{place}. {row[1]}: {row[0]} poäng")
        place += 1
    lines.append("")
    lines.append("Vinnare: " + results[0][1])

    _g()["results_text"] = "\n".join(lines)
    _g()["screen"] = "end"


def _advance_turn():
    _reset_turn_state()

    _g()["current_player_index"] += 1
    if _g()["current_player_index"] >= len(_g()["players"]):
        _g()["current_player_index"] = 0
        _g()["round_number"] += 1

    if _check_game_end():
        return

    _process_bot_turns()


def _process_bot_turns():
    while _g()["screen"] == "game" and _is_current_player_bot():
        scorecard = _current_scorecard()
        dice, keep, roll_count, options, category, score = execute_bot_turn(
            _g()["dice"], _g()["keep"], _g()["roll_count"], scorecard
        )
        _g()["dice"] = dice
        _g()["keep"] = keep
        _g()["roll_count"] = roll_count
        _g()["options"] = options
        scorecard[category] = score

        _reset_turn_state()
        _g()["current_player_index"] += 1
        if _g()["current_player_index"] >= len(_g()["players"]):
            _g()["current_player_index"] = 0
            _g()["round_number"] += 1

        if _check_game_end():
            return


def _format_protocol_text(scorecard):
    lines = []
    for cat in CATEGORIES:
        val = scorecard[cat]
        if val is None:
            lines.append(f"{cat:<12}: -")
        else:
            lines.append(f"{cat:<12}: {val}")

    lines.append("")
    lines.append(f"Övre summa: {get_upper_sum(scorecard)}")
    lines.append(f"Bonus: {get_bonus(scorecard)}")
    lines.append(f"Total: {get_total_score(scorecard)}")
    return "\n".join(lines)


def render_start_screen():
    st.title("Yatzy")

    _show_flash()

    player_count = st.selectbox(
        "Hur många spelare? (1-6):",
        options=list(range(1, 7)),
        index=_g()["player_count"] - 1,
        key="select_player_count",
    )
    _g()["player_count"] = player_count

    st.write("**Spelarnamn**")
    for i in range(player_count):
        name_col, bot_col = st.columns([4, 1], vertical_alignment="bottom")
        with name_col:
            name = st.text_input(
                f"Spelare {i + 1}:",
                value=_g()["player_names"][i],
                key=f"player_name_{i}",
            )
            _g()["player_names"][i] = name
        with bot_col:
            is_bot = st.checkbox("Bot", value=_g()["player_bots"][i], key=f"player_bot_{i}")
            _g()["player_bots"][i] = is_bot

    if st.button("Starta spel"):
        players = []
        is_bot = {}
        i = 0
        while i < player_count:
            name = _g()["player_names"][i].strip()
            if name == "":
                name = f"Spelare{i + 1}"
            players.append(name)
            is_bot[name] = bool(_g()["player_bots"][i])
            i += 1

        scorecards = {}
        for name in players:
            scorecards[name] = {cat: None for cat in CATEGORIES}

        _g()["players"] = players
        _g()["is_bot"] = is_bot
        _g()["scorecards"] = scorecards
        _g()["current_player_index"] = 0
        _g()["round_number"] = 1
        _reset_turn_state()
        _g()["screen"] = "game"
        _g()["confirm_exit"] = False
        _process_bot_turns()
        st.rerun()


def render_game_screen():
    player_name = _current_player_name()
    is_bot = _is_current_player_bot()
    scorecard = _current_scorecard()

    header_l, header_r = st.columns([5, 1], vertical_alignment="center")
    with header_l:
        st.write(f"**Spelare: {player_name}    Runda: {_g()['round_number']}/15**")
    with header_r:
        if st.button("Avsluta", use_container_width=True):
            _g()["confirm_exit"] = True

    if _g()["confirm_exit"]:
        st.warning("Vill du avsluta spelet?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Ja, avsluta", use_container_width=True):
                st.session_state.game = _default_state()
                st.rerun()
        with c2:
            if st.button("Nej, fortsätt", use_container_width=True):
                _g()["confirm_exit"] = False
                st.rerun()
        return

    _show_flash()

    if is_bot:
        st.info(f"{player_name} (bot) spelar just nu...")
        _process_bot_turns()
        st.rerun()
        return

    st.write("**Tärningar**")
    _, dice_block, _ = st.columns([0.5, 5, 0.5])
    with dice_block:
        dice_cols = st.columns(5, gap="small")
        new_keep = list(_g()["keep"])
        for i in range(5):
            with dice_cols[i]:
                num_l, num_c, num_r = st.columns([1, 1, 1])
                with num_c:
                    st.markdown(f"### {_dice_display(_g()['dice'][i])}")
                kept = st.checkbox("Spara", value=_g()["keep"][i], key=f"keep_{i}")
                new_keep[i] = kept
        _g()["keep"] = new_keep

    btn_col, info_col = st.columns([1, 4], vertical_alignment="center")
    with btn_col:
        roll_disabled = _g()["roll_count"] >= 3
        if st.button("Kasta", disabled=roll_disabled, use_container_width=True):
            if _g()["roll_count"] >= 3:
                _set_flash("Du har redan kastat 3 gånger.", "info")
            else:
                _g()["dice"] = roll_dice(list(_g()["dice"]), list(_g()["keep"]))
                _g()["roll_count"] += 1
                _g()["options"] = get_score_options(_g()["dice"])
            st.rerun()
    with info_col:
        rolls_left = 3 - _g()["roll_count"]
        st.write(f"Kast kvar: {rolls_left}")

    st.write("**Välj rad**")
    available = get_available_categories(scorecard)

    if _g()["roll_count"] == 0:
        register_disabled = True
        category_options = []
        selected_category = None
        suggested = 0
        st.selectbox(
            "Tillgängliga rader",
            options=["Kasta först för att se poängförslag."],
            key="category_select_empty",
        )
    else:
        category_options = available
        register_disabled = False
        labels = [f"{cat}  (förslag: {_g()['options'].get(cat, 0)})" for cat in category_options]
        selected_label = st.selectbox(
            "Tillgängliga rader",
            options=labels,
            key="category_select",
        )
        selected_index = labels.index(selected_label)
        selected_category = category_options[selected_index]
        suggested = _g()["options"].get(selected_category, 0)

    score_col, btn_col = st.columns([2, 1], vertical_alignment="bottom")
    with score_col:
        if category_options:
            score_text = st.text_input(
                "Poäng (0=stryk)",
                value=str(suggested),
                key=f"score_{selected_category}_{_g()['roll_count']}",
            )
        else:
            score_text = st.text_input(
                "Poäng (0=stryk)",
                value="",
                disabled=True,
                key="score_input_disabled",
            )
    with btn_col:
        if st.button("Registrera", disabled=register_disabled, use_container_width=True):
            if _g()["roll_count"] == 0:
                _set_flash("Du måste kasta minst en gång innan du registrerar.", "info")
                st.rerun()

            text = score_text.strip()
            if text == "":
                _set_flash("Skriv en poäng (0=stryk eller förslaget).", "info")
                st.rerun()

            try:
                score = int(text)
            except ValueError:
                _set_flash("Poäng måste vara ett heltal.", "error")
                st.rerun()

            if score != 0 and score != suggested:
                _set_flash("Ogiltigt. Välj 0 (stryk) eller exakt förslaget.", "error")
                st.rerun()

            scorecard[selected_category] = score
            _advance_turn()
            st.rerun()

    st.write("**Protokoll (aktuell spelare)**")
    st.text_area(
        "Protokoll",
        value=_format_protocol_text(scorecard),
        height=250,
        disabled=True,
        label_visibility="collapsed",
    )


def render_end_screen():
    st.title("Spelet är slut!")
    _show_flash()

    st.text(_g()["results_text"])

    protocol = build_protocol_text(_g()["players"], _g()["scorecards"])

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.download_button(
            label="Spara protokoll",
            data=protocol,
            file_name="yatzy_protokoll.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with btn_col2:
        if st.button("Till start", use_container_width=True):
            st.session_state.game = _default_state()
            st.rerun()


def main():
    st.set_page_config(page_title="Yatzy", layout="centered")
    init_session_state()

    screen = _g()["screen"]
    if screen == "start":
        render_start_screen()
    elif screen == "game":
        render_game_screen()
    elif screen == "end":
        render_end_screen()


if __name__ == "__main__":
    main()
