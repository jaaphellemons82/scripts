
import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import json
from contextlib import contextmanager
import opstelling

# === CONFIG INLADEN ===
with open("config.json") as f:
    cfg = json.load(f)

team = cfg["teams"][0]

# === GOOGLE SHEETS CONNECTIE ===
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# === SPELERSTABBLAD OPENEN ===
spelers_sheet = client.open_by_key(team["spreadsheet_id"]).worksheet(team["sheet_name_spelers"])
spelers_data = spelers_sheet.get_all_records()
df_spelers = pd.DataFrame(spelers_data)

df_spelers = opstelling.prepare_spelers(df_spelers)

if "opstelling" not in st.session_state:
    opst, bank = opstelling.genereer_opstelling(df_spelers)
    st.session_state["opstelling"] = opst
    st.session_state["bank"] = bank
    st.session_state["minutes"] = {s: 0 for s in df_spelers["Speler"]}
    st.session_state["wissels"] = {s: [] for s in df_spelers["Speler"]}
    st.session_state["info"] = {row["Speler"]: row for _, row in df_spelers.iterrows()}
    st.session_state["last_update"] = 0
    st.session_state["wissel_log"] = []
else:
    st.session_state.setdefault("wissel_log", st.session_state.get("wissel_log", []))

st.title(f"Opstelling {team['name']}")

veld = st.session_state["opstelling"]

SUGGESTION_STYLES = """
<style>
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .section-card) {
    border: 3px solid #0b1936;
    background: #ffffff;
    border-radius: 18px;
    padding: 1.4rem 1.6rem 1.8rem;
    margin-bottom: 2rem;
    box-shadow: 0 8px 18px rgba(11, 25, 54, 0.12);
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .section-card) > div[data-testid="stElementContainer"]:first-child {
    margin-bottom: 1.2rem;
}
.section-card {
    margin: 0;
    border: none;
    background: transparent;
    padding: 0;
}
.section-header {
    background: #0b6ec7;
    color: white;
    padding: 0.75rem 1.3rem;
    font-weight: 700;
    border-radius: 16px;
    letter-spacing: 0.02em;
    box-shadow: 0 3px 10px rgba(11, 110, 199, 0.25);
}
.suggestion-table {
    border: 3px solid #0b1936;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(11, 110, 199, 0.15);
}
.suggestion-header {
    background: #0b6ec7;
    color: white;
    padding: 0.6rem 1rem;
    font-weight: 700;
    font-size: 1.05rem;
}
.suggestion-head-cell { font-weight: 600; font-size: 0.85rem; }
.suggestion-head-cell.arrow { text-align: center; }
.suggestion-head-cell.action { text-align: right; }
.suggestion-empty {
    padding: 1rem;
    background: #e9f2ff;
    color: #0b6ec7;
    font-style: italic;
}
.suggestion-cell { font-weight: 600; color: #0b1936; }
.suggestion-cell.reason { font-weight: 400; font-size: 0.85rem; }
.suggestion-cell.arrow { color: #0b6ec7; font-size: 1.1rem; }
.suggestion-cell.action .stNumberInput input {
    background: #f4f7fb;
    border-radius: 6px;
    border: 1px solid #0b6ec7;
    color: #0b1936;
    font-weight: 600;
}
.suggestion-cell.action .stButton button {
    background: #0b6ec7;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.35rem 0.9rem;
    font-weight: 600;
}
.suggestion-cell.action .stButton button:hover {
    background: #0956a0;
}
</style>
"""

st.markdown(SUGGESTION_STYLES, unsafe_allow_html=True)


def show_line(*positions: str) -> None:
    cols = st.columns(len(positions))
    for col, pos in zip(cols, positions):
        naam = veld.get(pos, "")
        with col:
            st.markdown(
                "<div style='text-align:center;font-weight:bold;border:1px solid #ccc;padding:8px;border-radius:8px;background:#eaf4ff'>"
                + naam
                + "</div>",
                unsafe_allow_html=True,
            )


def _update_minutes_until(tijdstip: int) -> bool:
    last = st.session_state["last_update"]
    if tijdstip < last:
        st.error(f"Minuut {tijdstip} is kleiner dan de laatste update ({last}). Pas dit aan.")
        return False

    delta = tijdstip - last
    if delta > 0:
        for naam_labeled in st.session_state["opstelling"].values():
            naam = opstelling._name_only(naam_labeled)
            if naam and not naam.startswith("NIEMAND"):
                st.session_state["minutes"].setdefault(naam, 0)
                st.session_state["minutes"][naam] += delta
    st.session_state["last_update"] = tijdstip
    return True


def _find_position(spelernaam: str) -> str | None:
    for pos, naam in st.session_state["opstelling"].items():
        if opstelling._name_only(naam) == spelernaam:
            return pos
    return None


def _log_wissel(minuut: int, speler_out: str, speler_in: str, positie: str | None, bron: str) -> None:
    st.session_state["wissel_log"].append(
        {
            "Minuut": minuut,
            "Uit": speler_out,
            "In": speler_in,
            "Positie": positie or "-",
            "Bron": bron,
        }
    )


@contextmanager
def section_card(title: str):
    outer = st.container()
    with outer:
        st.markdown(
            f"<div class='section-card'><div class='section-header'>{title}</div><div class='section-body'>",
            unsafe_allow_html=True,
        )
        inner = st.container()
        with inner:
            yield
        st.markdown("</div></div>", unsafe_allow_html=True)


with section_card("Veldopstelling (4-3-3)"):
    show_line("LW", "ST", "RW")
    show_line("CML", "CM", "CMR")
    show_line("LB", "CBL", "CBR", "RB")
    show_line("GK")

with section_card("Bank"):
    st.write(", ".join(st.session_state["bank"]))

with section_card("Maak een wissel (handmatig)"):
    st.caption(f"Laatste update: minuut {st.session_state['last_update']}")

    speler_out = st.selectbox(
        "Speler uit veld", [opstelling._name_only(v) for v in st.session_state["opstelling"].values()]
    )
    speler_in = st.selectbox("Speler van bank", st.session_state["bank"])

    manual_input_key = "manual_minute_input"
    manual_suggest_key = "manual_minute_suggest"

    suggested_manual_minute = min(90, st.session_state["last_update"] + 5)
    if (
        manual_suggest_key not in st.session_state
        or st.session_state[manual_suggest_key] < st.session_state["last_update"]
    ):
        st.session_state[manual_suggest_key] = suggested_manual_minute

    manual_default = st.session_state.get(manual_input_key, st.session_state[manual_suggest_key])

    tijdstip_manual = st.number_input(
        "Minuut",
        min_value=1,
        max_value=90,
        value=manual_default,
        key=manual_input_key,
    )

    if st.button("Wissel uitvoeren (handmatig)"):
        tijdstip_int = int(tijdstip_manual)
        positie = _find_position(speler_out)
        if positie is None:
            st.error("Speler niet gevonden in huidige veldopstelling.")
        elif _update_minutes_until(tijdstip_int):
            ok = opstelling.wissel_speler(
                st.session_state["opstelling"],
                st.session_state["bank"],
                speler_out,
                speler_in,
                st.session_state["info"],
                st.session_state["minutes"],
                tijdstip_int,
            )
            if ok:
                st.session_state["minutes"].setdefault(speler_in, 0)
                st.session_state["wissels"].setdefault(speler_out, []).append(tijdstip_int)
                st.session_state["wissels"].setdefault(speler_in, []).append(tijdstip_int)
                _log_wissel(tijdstip_int, speler_out, speler_in, positie, "Handmatig")
                st.session_state[manual_suggest_key] = min(90, tijdstip_int + 5)
                st.session_state.pop(manual_input_key, None)
                st.success(f"Wissel uitgevoerd: {speler_out} -> {speler_in} ({tijdstip_int}')")
                st.rerun()
            else:
                st.error("Wissel niet mogelijk.")

with section_card("Posities wisselen (veld)"):
    field_positions = [pos for pos in opstelling._POS_ORDER if pos in st.session_state["opstelling"]]
    bezette_posities = [
        pos
        for pos in field_positions
        if st.session_state["opstelling"].get(pos, "").strip()
        and not st.session_state["opstelling"][pos].startswith("NIEMAND")
    ]
    if len(bezette_posities) < 2:
        st.caption("Niet genoeg veldspelers om te wisselen.")
    else:
        def format_position(option: str) -> str:
            waarde = st.session_state["opstelling"].get(option, "").strip()
            if not waarde:
                return f"{option} - leeg"
            if waarde.startswith("NIEMAND"):
                return f"{option} - {waarde}"
            return f"{waarde} [{option}]"

        pos1 = st.selectbox(
            "Speler/positie 1",
            bezette_posities,
            format_func=format_position,
            key="swap_pos1",
        )
        beschikbare_pos2 = [p for p in bezette_posities if p != pos1]
        pos2 = st.selectbox(
            "Speler/positie 2",
            beschikbare_pos2,
            format_func=format_position,
            key="swap_pos2",
        )

        if st.button("Posities omwisselen", key="swap_button"):
            if pos1 == pos2:
                st.warning("Kies twee verschillende posities.")
            else:
                speler1_label = st.session_state["opstelling"].get(pos1, "")
                speler2_label = st.session_state["opstelling"].get(pos2, "")
                st.session_state["opstelling"][pos1], st.session_state["opstelling"][pos2] = (
                    st.session_state["opstelling"][pos2],
                    st.session_state["opstelling"][pos1],
                )
                st.success(
                    f"Posities gewisseld: {speler1_label or pos1} <-> {speler2_label or pos2}"
                )
                st.rerun()




def voorgestelde_wissels(current_field, bank, info, minutes, max_per_group=3):
    voorstellen = {}
    groepen = {
        "Aanval": ["LW", "ST", "RW"],
        "Middenveld": ["CML", "CM", "CMR"],
        "Verdediging": ["LB", "CBL", "CBR", "RB"],
    }
    for groep, posities in groepen.items():
        group_suggestions = []
        veldspelers = []
        for pos in posities:
            speler_out = opstelling._name_only(current_field.get(pos, ""))
            if speler_out and speler_out in info:
                veldspelers.append((speler_out, pos, minutes.get(speler_out, 0)))
        veldspelers.sort(key=lambda x: -x[2])

        kandidaten_bank = [naam for naam in bank if naam in info]
        kandidaten_bank.sort(key=lambda naam: minutes.get(naam, 0))

        for speler_out, pos, _ in veldspelers:
            for speler_in in kandidaten_bank:
                s_info = info.get(speler_in, {})
                posities_in = set(s_info.get("Favorieten", [])) | set(s_info.get("Alternatief", []))
                standin_target = str(s_info.get("Standin", "")).strip()
                if standin_target:
                    posities_in.add(standin_target)

                if pos in posities_in and opstelling._can_play(s_info, pos):
                    reden = (
                        f"{speler_in} weinig minuten ({minutes.get(speler_in, 0)}), "
                        f"{speler_out} veel minuten ({minutes.get(speler_out, 0)})"
                    )
                    group_suggestions.append(
                        {
                            "Groep": groep,
                            "Speler in": speler_in,
                            "Speler uit": speler_out,
                            "Positie": pos,
                            "Reden": reden,
                        }
                    )
                    break
            if len(group_suggestions) >= max_per_group:
                break
        voorstellen[groep] = group_suggestions
    return voorstellen


with section_card("Voorgestelde wissels (per linie)"):
    voorstellen = voorgestelde_wissels(
        st.session_state["opstelling"],
        st.session_state["bank"],
        st.session_state["info"],
        st.session_state["minutes"],
        max_per_group=3,
    )

    for groep, wissels in voorstellen.items():
        block = st.container()
        with block:
            st.markdown("<div class='suggestion-table'>", unsafe_allow_html=True)
            st.markdown(f"<div class='suggestion-header'>{groep}</div>", unsafe_allow_html=True)

            head_cols = st.columns([2, 0.6, 2, 4, 2])
            head_cols[0].markdown("<div class='suggestion-head-cell'>Speler uit</div>", unsafe_allow_html=True)
            head_cols[1].markdown("<div class='suggestion-head-cell arrow'>?</div>", unsafe_allow_html=True)
            head_cols[2].markdown("<div class='suggestion-head-cell'>Speler in</div>", unsafe_allow_html=True)
            head_cols[3].markdown("<div class='suggestion-head-cell'>Reden</div>", unsafe_allow_html=True)
            head_cols[4].markdown("<div class='suggestion-head-cell action'>Actie</div>", unsafe_allow_html=True)

            if not wissels:
                st.markdown(
                    "<div class='suggestion-empty'>Geen wisselvoorstellen beschikbaar voor deze linie.</div>",
                    unsafe_allow_html=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)
                continue

            for idx, voorstel in enumerate(wissels):
                row_bg = "#a3c9f7" if idx % 2 else "#ffffff"
                tijd_key = f"tijd_{groep}_{idx}"
                suggest_key = f"suggest_{tijd_key}"

                default_minute = min(90, st.session_state["last_update"] + 5)
                if (
                    suggest_key not in st.session_state
                    or st.session_state[suggest_key] < st.session_state["last_update"]
                ):
                    st.session_state[suggest_key] = default_minute

                input_key = f"{tijd_key}_input"

                col1, col2, col3, col4, col5 = st.columns([2, 0.6, 2, 4, 2])
                col1.markdown(
                    f"<div class='suggestion-cell' style='background:{row_bg};'>{voorstel['Speler uit']}</div>",
                    unsafe_allow_html=True,
                )
                col2.markdown(
                    f"<div class='suggestion-cell arrow' style='background:{row_bg};'>?</div>",
                    unsafe_allow_html=True,
                )
                col3.markdown(
                    f"<div class='suggestion-cell' style='background:{row_bg};'>{voorstel['Speler in']}</div>",
                    unsafe_allow_html=True,
                )
                col4.markdown(
                    f"<div class='suggestion-cell reason' style='background:{row_bg};'>{voorstel['Reden']}</div>",
                    unsafe_allow_html=True,
                )

                with col5:
                    st.markdown(
                        f"<div class='suggestion-cell action' style='background:{row_bg};'>",
                        unsafe_allow_html=True,
                    )
                    form_key = f"form_{tijd_key}"
                    with st.form(form_key):
                        minute_value = st.number_input(
                            "Minuut",
                            min_value=1,
                            max_value=90,
                            value=int(st.session_state[suggest_key]),
                            step=1,
                            key=input_key,
                            label_visibility="collapsed",
                        )
                        submitted = st.form_submit_button("Wissel", use_container_width=True)
                        if submitted:
                            tijdstip_int = int(minute_value)
                            if _update_minutes_until(tijdstip_int):
                                ok = opstelling.wissel_speler(
                                    st.session_state["opstelling"],
                                    st.session_state["bank"],
                                    voorstel["Speler uit"],
                                    voorstel["Speler in"],
                                    st.session_state["info"],
                                    st.session_state["minutes"],
                                    tijdstip_int,
                                )
                                if ok:
                                    st.session_state["minutes"].setdefault(voorstel["Speler in"], 0)
                                    st.session_state["wissels"].setdefault(voorstel["Speler uit"], []).append(tijdstip_int)
                                    st.session_state["wissels"].setdefault(voorstel["Speler in"], []).append(tijdstip_int)
                                    _log_wissel(
                                        tijdstip_int,
                                        voorstel["Speler uit"],
                                        voorstel["Speler in"],
                                        voorstel["Positie"],
                                        f"Voorstel {groep}",
                                    )
                                    st.session_state[suggest_key] = min(90, tijdstip_int + 5)
                                    st.session_state.pop(input_key, None)
                                    st.success(
                                        f"Wissel uitgevoerd: {voorstel['Speler uit']} ? {voorstel['Speler in']} ({tijdstip_int}')"
                                    )
                                    st.rerun()
                                else:
                                    st.error("Wissel niet mogelijk.")
                            else:
                                st.error("Ongeldige minuut ingevoerd.")
                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

with section_card("[SWAP] Doorgevoerde wissels"):
    if st.session_state["wissel_log"]:
        wissel_df = pd.DataFrame(st.session_state["wissel_log"])
        display_cols = ["Minuut", "Uit", "In", "Positie", "Bron"]
        for kolom in display_cols:
            if kolom not in wissel_df.columns:
                wissel_df[kolom] = ""
        wissel_df = wissel_df[display_cols].sort_values("Minuut").reset_index(drop=True)
        st.dataframe(wissel_df, hide_index=True)
    else:
        st.caption("Nog geen wissels doorgevoerd.")

with section_card("[TIME] Speeltijd & Wissels"):
    stats_data = []
    for speler, minuten in st.session_state["minutes"].items():
        wisselmomenten = st.session_state["wissels"].get(speler, [])
        stats_data.append(
            {
                "Speler": speler,
                "Minuten": minuten,
                "Aantal wissels": len(wisselmomenten),
                "Momenten": ", ".join(str(m) for m in wisselmomenten),
            }
        )

    if stats_data:
        df_stats = pd.DataFrame(stats_data).sort_values("Speler").reset_index(drop=True)
        st.dataframe(df_stats, hide_index=True)
    else:
        st.caption("Nog geen speeltijd geregistreerd.")

