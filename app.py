import streamlit as st
import pandas as pd
import random
import re, os
from streamlit_sortables import sort_items
from difflib import get_close_matches

# import your existing functions
from geography_game import (
    generate_match_question,
    get_random_pair,
    is_good_guess,
    odd_one_out,
    ranking_question,
    daily_challenge,
    swipe_pair,
    choose_place,
    _load_symmetric
)

# ========================
# SAME SAFE FILENAME LOGIC
# ========================
def safe_filename(name):
    name = name.replace(" ", "_")
    name = re.sub(r'[^a-zA-Z0-9_()\-]', '', name)
    if(GAME_TYPE=="SHAPE"):
        return f"{name}.svg"
    else:
        return f"{name}.png"


# ========================
# LOAD SVG FROM FOLDER
# ========================
def load_svg(name, folder="outline_svgs"):
    filename = safe_filename(name)
    path = os.path.join(folder, filename)

    if not os.path.exists(path):
        st.error(f"Missing SVG: {name}")
        return None

    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def suggest_countries(input_text, options, n=5):
    if not input_text:
        return []
    
    input_text = input_text.lower()
    
    matches = [o for o in options if input_text in o.lower()]    
    return matches[:n]

def simplify_svg(svg, keep_every=3):
    match = re.search(r'd="([^"]+)"', svg)
    if not match:
        return svg

    path = match.group(1)

    # split into commands and numbers
    tokens = re.findall(r'[A-Za-z]|-?\d+\.?\d*', path)

    new_tokens = []
    coords = []
    current_cmd = None

    for t in tokens:
        if t.isalpha():
            # flush previous coords
            if coords:
                # group into (x,y) pairs
                pairs = list(zip(coords[::2], coords[1::2]))
                reduced = pairs[::keep_every]

                for x, y in reduced:
                    new_tokens.extend([x, y])

                coords = []

            # keep command
            new_tokens.append(t)
            current_cmd = t

        else:
            coords.append(t)

    # flush remaining coords
    if coords:
        pairs = list(zip(coords[::2], coords[1::2]))
        reduced = pairs[::keep_every]
        for x, y in reduced:
            new_tokens.extend([x, y])

    new_path = " ".join(new_tokens)
    return svg.replace(path, new_path)
# ========================
# RENDER SVG (CLEAN UI)
# ========================
def render(name, size=350, angle=0, blur=0):
    #render_img(name, size=350, angle=0, blur=0):
    if(GAME_TYPE=="SHAPE"):
        return render_svg(load_svg(name),  angle=angle)
    elif(GAME_TYPE=="FLAG"):
        return render_img(name, size, angle, blur=blur)
def render_svg(svg, size=350, angle=0, blur=0):
    return f"""
    <div style="
        width:{size}px;
        height:{size}px;
        display:flex;
        align-items:center;
        justify-content:center;
        border:1px solid #ddd;
        border-radius:10px;
        background:white;
        margin:auto;
    ">
        <div style="transform: rotate({angle}deg); filter: blur({blur}px); transition: transform 0.1s;">
            {svg}
    """

import base64
def render_img(name, size=350, angle=0, blur=0):
    folder="png_flags"
    filename = safe_filename(name)
    path = os.path.join(folder, filename)

    if not os.path.exists(path):
        st.error(f"Missing SVG: {name}")
        print(path)
        return None

    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    return f"""
    <div style="
        width:{size+100}px;
        height:{size+100}px;
        display:flex;
        align-items:center;
        justify-content:center;
        border:1px solid #ddd;
        border-radius:10px;
        background:white;
        margin:auto;
        overflow:hidden;
    ">
        <div style="
            transform: rotate({angle}deg);
            filter: blur({blur}px);
            transition: transform 0.1s;
            width:100%;
            height:100%;
            display:flex;
            align-items:center;
            justify-content:center;
        ">
            <img
                src="data:image/png;base64,{b64}"
                style="
                    max-width:100%;
                    max-height:100%;
                    object-fit:contain;
                    display:block;
                "
            >
        </div>
    </div>
    """
GAME_TYPE = "FLAG"

# ========================
# CONFIG
# ========================

st.set_page_config(page_title="Geography Game", layout="centered")
if(GAME_TYPE=="SHAPE"):
    CSV_FILE = "shape_similarity.csv"
elif(GAME_TYPE=="FLAG"):
    CSV_FILE = "flag_similarity.csv"


# ========================
# TITLE
# ========================
game_type = st.sidebar.selectbox(
    "Choose Game Type",
    [
        "Flags",
        "Outlines"
    ]
)


if game_type == "Flags":
    GAME_TYPE = "FLAG"
    CSV_FILE = "flag_similarity.csv"
    st.title("🚩 Flag Geography Game")
    st.markdown(f"Guess places based on **flag visual similarity** (color, layout, patterns)")   
elif game_type == "Outlines":
    GAME_TYPE = "SHAPE"
    CSV_FILE = "shape_similarity.csv"
    st.title("🌍 Shape Geography Game")
    st.markdown(f"Guess places based on **shape similarity** (IoU + rotation)")

mode = st.sidebar.selectbox(
    "Choose Game Mode",
    [
        "Match Question",
        "Higher / Lower",
        "Odd One Out",
        "Ranking",
        "Swipe Mode",
        "Blur Reveal",
        "Rotate Game",
        "Daily Challenge"
    ]
)
region = st.sidebar.selectbox(
    "Choose Region",
    [
    "World",
    "US States",
    "Europe",
    "Africa",
    "Asia",
    "North America",
    "South America",
    "Oceania",
    "Islands"
    ]
    )

dif_level = st.sidebar.selectbox(
    "Choose difficulty level",
    [
    "Easy",
    "Medium",
    "Hard"
    ]
)

# ========================
# MATCH QUESTION
# ========================

if mode == "Match Question":

    if "match_q" not in st.session_state:
        st.session_state.match_q = generate_match_question(CSV_FILE, region=region, dif_level=dif_level)
        st.session_state.angle = 0

    next_clicked = st.session_state.get("next_clicked", False)

    def next_question():
        st.session_state.match_q = generate_match_question(CSV_FILE, region=region, dif_level=dif_level)
        st.session_state.angle = 0
        st.session_state.next_clicked = False

    q = st.session_state.match_q
    question = f"What looks most like {q['base']}?"
    st.subheader(question)

    choice = st.radio("Choose:", q["choices"])

    angle = st.slider("Rotate shape", 0, 180, key="angle")
    #st.markdown(render_svg(load_svg(q["base"]),  angle=angle), unsafe_allow_html=True)
    #st.markdown(render_img("C:/Users/issac/Downloads/Nepal.png",  angle=angle), unsafe_allow_html=True)
    st.markdown(render(q["base"],  angle=angle), unsafe_allow_html=True)

    if st.button("Submit"):
        if choice == q["answer"]:
            st.success(f"✅ Correct! {q['answer']}'s score was {round(q['highest'], 3)}")
        else:
            st.error(f"❌ Wrong!")

    # if st.button("Next"):
    #     st.session_state.match_q = generate_match_question(CSV_FILE)
    #     st.rerun()
    st.button("Next", on_click=next_question)


# ========================
# HIGHER / LOWER
# ========================

elif mode == "Higher / Lower":

    if "pair_a" not in st.session_state:
        st.session_state.pair_a = get_random_pair(CSV_FILE)
        st.session_state.pair_b = get_random_pair(CSV_FILE)
        while True:
            a = get_random_pair(CSV_FILE)
            b = get_random_pair(CSV_FILE)

            dif = abs(a[2] - b[2])

            if dif_level == "Easy" and dif > 0.2:
                st.session_state.pair_a = a
                st.session_state.pair_b = b
                break

            elif dif_level == "Medium" and 0.1 < dif <= 0.2:
                st.session_state.pair_a = a
                st.session_state.pair_b = b
                break

            elif dif_level == "Hard" and dif <= 0.1:
                st.session_state.pair_a = a
                st.session_state.pair_b = b
                break
        st.session_state.indexA=random.randint(0,1)
        st.session_state.indexB=random.randint(0,1)

    def next_question():
        while True:
            a = get_random_pair(CSV_FILE)
            b = get_random_pair(CSV_FILE)

            dif = abs(a[2] - b[2])

            if dif_level == "Easy" and dif > 0.2:
                st.session_state.pair_a = a
                st.session_state.pair_b = b
                break

            elif dif_level == "Medium" and 0.1 < dif <= 0.2:
                st.session_state.pair_a = a
                st.session_state.pair_b = b
                break

            elif dif_level == "Hard" and dif <= 0.1:
                st.session_state.pair_a = a
                st.session_state.pair_b = b
                break
        st.session_state.indexA=random.randint(0,1)
        st.session_state.indexB=random.randint(0,1)

    a = st.session_state.pair_a
    b = st.session_state.pair_b
    dif = abs(a[2] - b[2])

    st.write(f"Pair A: {a[0]} vs {a[1]}")
    st.write(f"Pair B: {b[0]} vs {b[1]}")

    guess = st.radio(f"{round(dif,2)} Pair B is:", ["Higher", "Lower"])
    col1, col2 = st.columns(2)

    
    st.write(f"{a[st.session_state.indexA]}")
    #st.markdown(render_svg(load_svg(a[st.session_state.indexA]), size=200), unsafe_allow_html=True)
    st.markdown(render(a[st.session_state.indexA],  size=200), unsafe_allow_html=True)
    st.write(f"{b[st.session_state.indexB]}")
    #st.markdown(render_svg(load_svg(b[st.session_state.indexB]), size=200), unsafe_allow_html=True)
    st.markdown(render(b[st.session_state.indexB],  size=200), unsafe_allow_html=True)    

    if st.button("Check"):

        if (b[2] > a[2] and guess == "Higher") or \
           (b[2] < a[2] and guess == "Lower"):
            st.success("✅ Correct!")
            st.write(f"A IoU: {a[2]:.3f} | B IoU: {b[2]:.3f}")

        else:
            st.error("❌ Wrong!")


    st.button("Next", on_click=next_question)


# ========================
# ODD ONE OUT
# ========================

elif mode == "Odd One Out":
    if "odd" not in st.session_state:
        st.session_state.odd = odd_one_out(CSV_FILE, region=region)
        st.session_state.angle = 0
  

    def next_question():
        st.session_state.odd = odd_one_out(CSV_FILE, region=region)
        st.session_state.angle = 0

    base, choices, odd, odd_index = st.session_state.odd

    st.write(f"{'Shape' if game_type == 'Outlines' else 'Flag'} 1: **{base}**")
    choice = st.radio("Pick the odd one:", choices)
    angle = st.slider("Rotate shape", 0, 180, key="angle")
    #st.markdown(render_svg(load_svg(base),  angle=angle), unsafe_allow_html=True)
    st.markdown(render(base, angle=angle), unsafe_allow_html=True)

    if st.button("Submit"):
        if choice == odd:
            st.success(f"✅ Correct! {odd} was # {odd_index}")
        else:
            st.error(f"❌ Wrong!")

    st.button("Next", on_click=next_question)


# ========================
# RANKING
# ========================
elif mode == "Ranking":

    # ------------------------
    # INIT STATE
    # ------------------------
    if "ranking" not in st.session_state:
        st.session_state.ranking = ranking_question(CSV_FILE, region=region, dif_level=dif_level)

        st.session_state.checked = False
        st.session_state.last_order = []
        st.session_state.angle = 0
    if "attempts" not in st.session_state:
        st.session_state.attempts = 0
    
    def next_question():
        st.session_state.attempts = 0
        st.session_state.ranking = ranking_question(CSV_FILE,region= region, dif_level=dif_level)

        st.session_state.checked = False
        st.session_state.last_order = []
        st.session_state.angle = 0


    base, correct_order, options = st.session_state.ranking
    

    # ------------------------
    # UI
    # ------------------------
    st.subheader(f"Rank by similarity to: {base}")
    angle = st.slider("Rotate shape", 0, 180, key="angle")
    #st.markdown(render_svg(load_svg(base),  angle=angle), unsafe_allow_html=True)
    st.markdown(render(base, angle=angle), unsafe_allow_html=True)
    st.write(f"Attempts: {st.session_state.attempts}")

    ordered = sort_items(options, direction="vertical")

    # ------------------------
    # CHECK BUTTON
    # ------------------------
    if st.button("Check"):
        st.session_state.checked = True
        st.session_state.attempts += 1
        st.session_state.last_order = ordered

    # ------------------------
    # RESULT DISPLAY
    # ------------------------
    if st.session_state.checked:
        st.write("### Result:")

        user_order = st.session_state.last_order

        score = 0

        for i, item in enumerate(user_order):
            if item == correct_order[i]:
                color = "#4CAF50"  # green
                icon = "✅"
                score += 1
            else:
                color = "#FFC107"  # yellow
                icon = "⚠️"

            st.markdown(
                f"<div style='padding:10px; margin:5px; background:{color}; border-radius:10px;'>"
                f"{icon} {item}"
                f"</div>",
                unsafe_allow_html=True
            )

        # Score summary
        st.write(f"**Score: {score}/{len(correct_order)}**")

        if score == len(correct_order):
            st.success(f"🎉 Perfect ranking! It took you {st.session_state.attempts} attempts")
        elif score >= len(correct_order) - 1:
            st.success("🔥 Very close!")
        else:
            st.error("❌ Not quite right")

    # ------------------------
    # NEXT BUTTON
    # ------------------------
    st.button("Next", on_click=next_question)

# ========================
# DAILY CHALLENGE
# ========================

elif mode == "Daily Challenge":

    import datetime
    today = str(datetime.date.today())
    if "daily" not in st.session_state:
        st.session_state.daily = daily_challenge(today, CSV_FILE)
    if "slider_min" not in st.session_state:
        st.session_state.slider_min = 0.0
        st.session_state.slider_max = 1.0
    if "attempts" not in st.session_state:
        st.session_state.attempts = 0

    a, b, score = st.session_state.daily

    st.subheader("Today's Challenge")

    st.write(f"Guess the similarity between:")
    st.write(f"**{a} vs {b}**")
    st.write(f"Attempts: {st.session_state.attempts}")

    guess = st.slider("Your guess (IoU)", st.session_state.slider_min, st.session_state.slider_max)

    if st.button("Submit"):
        st.session_state.attempts += 1
        st.write(f"Actual IoU: {score:.3f}")

        diff = abs(score - guess)

        if diff < 0.05:
            st.success(f"🔥 Amazing! It took you {st.session_state.attempts} guesses")
        elif diff < 0.1:
            st.success(f"👍 Close!  It took you {st.session_state.attempts} guesses")
        else:
            if guess < score:
                st.error("❌ Not close! Try a higher guess")
                #st.session_state.slider_min = min(1.0, guess+diff*0.5)
            else:
                st.error("❌ Not close! Try a lower guess")
                #st.session_state.slider_max = max(0.0, guess-diff*0.5)

elif mode == "Swipe Mode":
    percent = {
    "Easy": 0.15,
    "Medium": 0.08,
    "Hard": 0.03
    }[dif_level]
    if "swipe" not in st.session_state:
        st.session_state.swipe = swipe_pair(CSV_FILE, percent=percent, region=region)
    if "angle" not in st.session_state:
        st.session_state.angle = 0

    def next_question():
        st.session_state.swipe = swipe_pair(CSV_FILE, compare, percent=percent, region=region)
        st.session_state.angle = 0
    def handle_answer_iou(choice):
        actual = iou >= 0.6
        if(choice == actual):
            st.success(f"✅ Correct! IoU was {round(iou,2)}")
        else:
            st.error(f"❌ Wrong! IoU was {round(iou,2)}")
    def handle_answer_per(choice):
        if choice == top_per:
            st.success(f"✅ Correct! It was {'in' if top_per else 'not in'} the top {round(percent*100)}%")
        else:
            st.error(f"❌ Wrong! It was {'in' if top_per else 'not in'} the top {round(percent*100)}%")

    base, compare, iou, top_per = st.session_state.swipe

    st.write(f"{'Shape' if game_type == 'Outlines' else 'Flag'} 1: **{base}**")
    angle = st.slider("Rotate shape", 0, 180, key="angle")
    #st.markdown(render_svg(load_svg(base),  angle=angle), unsafe_allow_html=True)
    st.markdown(render(base,  angle=angle), unsafe_allow_html=True)
    st.write(f"Is **{compare}** a similar {'shape' if game_type == 'Outlines' else 'flag'}?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("👎 Not Similar", use_container_width=True):
            handle_answer_per(False)

    with col2:
        if st.button("👍 Similar", use_container_width=True):
            handle_answer_per(True)

    st.button("Next", on_click=next_question)


elif mode == "Blur Reveal":
    BLUR_SETTINGS = {
    "Easy": {
        "start": 4,
        "step": 2
    },
    "Medium": {
        "start": 8,
        "step": 3
    },
    "Hard": {
        "start": 12,
        "step": 4
    }
}

    if "blur_q" not in st.session_state:
        st.session_state.blur_q = choose_place(CSV_FILE, region=region)
        st.session_state.blur_level = BLUR_SETTINGS[dif_level]["start"]
        st.session_state.attempts = 0
        st.session_state.guess = ""
        st.session_state.set_guess = None
        st.session_state.feedback = None
    
    
    if st.session_state.set_guess is not None:
        st.session_state.guess = st.session_state.set_guess
        st.session_state.set_guess = None


# show previous feedback
    if st.session_state.feedback is not None:
        if st.session_state.feedback["type"] == "error":
            st.error(st.session_state.feedback["msg"])
        else:
            st.success(st.session_state.feedback["msg"])

    def next_question():
        st.session_state.blur_q = choose_place(CSV_FILE, region=region)
        st.session_state.blur_level = BLUR_SETTINGS[dif_level]["start"]
        st.session_state.attempts = 0
        st.session_state.guess = ""
        st.session_state.set_guess = None
        st.session_state.feedback = None

    shape = st.session_state.blur_q
    blur = st.session_state.blur_level

    st.subheader("Guess the place!")

    st.markdown(
        render(shape, blur=blur),
        unsafe_allow_html=True
    )
    #all_shapes = pd.read_csv(CSV_FILE)["shape1"].unique().tolist()
    all_shapes = _load_symmetric(CSV_FILE)["shape1"].unique().tolist()
    guess = st.text_input("Your guess:", key="guess")

    suggestions = suggest_countries(guess, all_shapes)
    if suggestions:
        st.write("Suggestions:")

        cols = st.columns(len(suggestions))
        for i, s in enumerate(suggestions):
            if cols[i].button(s):
                st.session_state.set_guess = s   # 🔥 THIS updates the input
                st.rerun()                   # 🔥 forces UI refresh


    
    # if st.button("Submit"):
    #     st.session_state.attempts += 1

    #     if guess.lower() == shape.lower():
    #         st.success(f"✅ Correct! You got it in {st.session_state.attempts} guesses")
    #     else:
    #         blur = max(0, blur - BLUR_SETTINGS[dif_level]["step"])
    #         st.session_state.blur_level = blur
    #         st.error("❌ Try again")
    

    if st.button("Submit"):
        st.session_state.attempts += 1
        if guess.lower() == shape.lower():

            st.session_state.feedback = {
                "type": "success",
                "msg": f"✅ Correct! You got it in {st.session_state.attempts} guesses"
            }
        else:
            st.session_state.feedback = {
                "type": "error",
                "msg": "❌ Try again"
            }
            st.session_state.blur_level = max(0,blur - BLUR_SETTINGS[dif_level]["step"])
            st.rerun()

    st.button("Next", on_click=next_question)

elif mode == "Rotate Game":
    if "rotate_g" not in st.session_state:
        st.session_state.rotate_g = choose_place(CSV_FILE, region)
        st.session_state.attempts = 0
        st.session_state.angle = 0
        st.session_state.angleOffset = random.randint(30, 150)
        st.session_state.min_angle = 0
        st.session_state.max_angle = 180
    def next_question():
        st.session_state.rotate_g = choose_place(CSV_FILE, region)
        st.session_state.attempts = 0
        st.session_state.angle = 0
        st.session_state.angleOffset = random.randint(30, 150)
        st.session_state.min_angle = 0
        st.session_state.max_angle = 180
    
    rotate_g = st.session_state.rotate_g
    angle = st.slider("Rotate shape", st.session_state.min_angle, st.session_state.max_angle, key="angle")

    st.subheader(f"Rotate to the correct orientation!")

    #st.markdown(render_svg(load_svg(rotate_g), angle = (angle - st.session_state.angleOffset)),unsafe_allow_html=True)
    st.markdown(render(rotate_g,  angle=(angle - st.session_state.angleOffset)), unsafe_allow_html=True)
    if st.button("Submit"):
        st.session_state.attempts += 1
        tolerance = {
            "Easy": 25,
            "Medium": 15,
            "Hard": 5
        }[dif_level]
        if abs(angle - st.session_state.angleOffset) <= tolerance:
            st.success(f"✅ Correct! You got {rotate_g} in {st.session_state.attempts} guesses within {round(abs(angle - st.session_state.angleOffset),2)} degrees!")
        else:
            if(angle > st.session_state.angleOffset):
                st.error("❌ Try again! Try rotating left")
            else:
                st.error("❌ Try again! Try rotating right")
            
            #st.session_state.min_angle = max(0, int(angle - abs(angle - st.session_state.angleOffset)*.5))
            #st.session_state.max_angle = int(min(180, angle + abs(angle - st.session_state.angleOffset)*.5))
    st.button("Next", on_click=next_question)
