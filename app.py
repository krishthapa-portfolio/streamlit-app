import streamlit as st
import pandas as pd

st.set_page_config(page_title="Daily Recommendation System", page_icon="📅", layout="centered")

# -----------------------------
# 1) Historical Data 
# -----------------------------

student_history = pd.DataFrame({
    "study_sessions": [2,3,2,4,3,2],
    "gym_sessions":   [1,0,1,1,0,1],
    "focus_success":  [0.7,0.8,0.6,0.85,0.75,0.7],
    "stress":         [3,4,3,5,2,3]
})

athlete_history = pd.DataFrame({
    "study_sessions":    [2,2,3,2,3],
    "practice_sessions": [1,1,1,1,1],
    "gym_sessions":      [1,1,2,1,2],
    "recovery_sessions": [1,1,1,0,1],
    "fatigue":           [3,4,3,5,3],
    "stress":            [3,4,4,5,3]
})

adult_history = pd.DataFrame({
    "work_hours":   [8,9,8,8,7],
    "gym_sessions": [1,0,1,1,0],
    "stress":       [3,4,3,5,2]
})

# -----------------------------
# 5) Helper Functions (UNCHANGED logic)
# -----------------------------

def explain_task(task, reason, context):
    return {"task": task, "reason": reason, "context": context}

def display_plan_section(label, tasks):
    st.markdown(f"**{label}**")
    for t in tasks:
        with st.expander(f"✅ {t['task']}"):
            st.markdown(f"**Reason:** {t['reason']}")
            st.markdown(f"**Context:** {t['context']}")
    st.markdown("")

def show_insights(role, sleep, stress_before, avg_stress):
    st.subheader("💡 Insights")
    insights = []
    if sleep < 6:
        insights.append("Low sleep reduces your focus and mental performance today. The plan shifts toward shorter, lighter tasks to help you stay productive without wearing out.")
    if stress_before >= 4:
        insights.append("Starting the day with high stress means recovery activities are a higher priority today to help bring your stress level down.")
    if avg_stress > 3:
        insights.append("Your stress has been consistently high based on your history. Building in more rest and recovery on a regular basis would help manage that pattern.")
    if role == "student":
        insights.append("Student pattern: how well your day goes depends heavily on managing your energy around classes and keeping a consistent study routine.")
    if role == "student_athlete":
        insights.append("Student-athlete pattern: practice is the biggest drain on your body each day. Scheduling recovery time around it is one of the most important things you can do.")
    if role == "adult":
        insights.append("Working adult pattern: work takes up the most time and energy in your day. What you choose to do after work should reflect how much you have left.")
    for insight in insights:
        st.info(insight)
    st.divider()
    with st.expander("📊 View historical data used for this analysis"):
        hist = {"student": student_history, "student_athlete": athlete_history, "adult": adult_history}
        st.dataframe(hist[role], use_container_width=True)

# -----------------------------
# Session state init
# -----------------------------

if "phase" not in st.session_state:
    st.session_state.phase = 1
if "data" not in st.session_state:
    st.session_state.data = {}

# ============================================================
# PHASE 1 — Collect inputs
# ============================================================

if st.session_state.phase == 1:

    st.title("📅 Daily Recommendation System")
    st.markdown("Enter your daily info below and get a personalized schedule recommendation.")
    st.divider()

    # 2) Role Selection
    st.subheader("Step 1 — Select your role")
    role_label = st.radio("Who are you?", ["Student", "Student-Athlete", "Working Adult"], horizontal=True)
    role = {"Student": "student", "Student-Athlete": "student_athlete", "Working Adult": "adult"}[role_label]

    st.divider()

    # 3) Daily Inputs
    st.subheader("Step 2 — Daily check-in")
    col1, col2, col3 = st.columns(3)
    sleep         = col1.number_input("Sleep hours", min_value=0.0, max_value=12.0, value=7.0, step=0.5)
    energy        = col2.slider("Energy level (1–5)", 1, 5, 3)
    stress_before = col3.slider("Stress level before day (1–5)", 1, 5, 2)

    st.divider()

    classes = []
    practice_today = "no"
    practice_start = practice_end = work_start = work_end = None

    if role in ["student", "student_athlete"]:
        st.subheader("Step 3 — Class schedule")
        num_classes = st.number_input("How many classes today?", min_value=0, max_value=8, value=2, step=1)
        for i in range(int(num_classes)):
            c1, c2 = st.columns(2)
            s = c1.text_input(f"Class {i+1} start time", value="9:00 AM",  key=f"cs_{i}")
            e = c2.text_input(f"Class {i+1} end time",   value="10:00 AM", key=f"ce_{i}")
            classes.append((s, e))

    if role == "student_athlete":
        st.subheader("Step 4 — Practice schedule")
        if st.checkbox("Do you have practice today?"):
            practice_today = "yes"
            pt1, pt2 = st.columns(2)
            practice_start = pt1.text_input("Practice start time", value="4:00 PM")
            practice_end   = pt2.text_input("Practice end time",   value="6:00 PM")

    if role == "adult":
        st.subheader("Step 3 — Work schedule")
        wc1, wc2 = st.columns(2)
        work_start = wc1.text_input("Work start time", value="9:00 AM")
        work_end   = wc2.text_input("Work end time",   value="5:00 PM")

    st.divider()

    if st.button("Generate pre-activity plan ▶", type="primary", use_container_width=True):
        avg_stress  = (athlete_history if role == "student_athlete" else student_history if role == "student" else adult_history)["stress"].mean()
        avg_fatigue = athlete_history["fatigue"].mean() if role == "student_athlete" else None
        st.session_state.data = dict(
            role=role, sleep=sleep, energy=energy, stress_before=stress_before,
            classes=classes, practice_today=practice_today,
            practice_start=practice_start, practice_end=practice_end,
            work_start=work_start, work_end=work_end,
            avg_stress=avg_stress, avg_fatigue=avg_fatigue
        )
        st.session_state.phase = 2
        st.rerun()

# ============================================================
# PHASE 2 — Pre-plan display, post check-in, full plan
# ============================================================

elif st.session_state.phase == 2:

    d             = st.session_state.data
    role          = d["role"]
    sleep         = d["sleep"]
    energy        = d["energy"]
    stress_before = d["stress_before"]
    classes       = d["classes"]
    practice_today  = d["practice_today"]
    practice_start  = d["practice_start"]
    practice_end    = d["practice_end"]
    work_start    = d["work_start"]
    work_end      = d["work_end"]
    avg_stress    = d["avg_stress"]

    st.title("📅 Daily Recommendation System")
    st.divider()
    st.success("Here is your plan for the first part of your day.")
    st.subheader("📋 Pre-Activity Plan")

    # ---- STUDENT pre-plan ----
    if role == "student":
        morning = []
        if sleep < 6:
            morning.append(explain_task(
                "Light Focus Study (30–45 min)",
                "Low sleep reduces your ability to focus and retain information for extended periods.",
                "Shorter study sessions help you stay productive without wearing out your concentration early in the day."
            ))
        else:
            morning.append(explain_task(
                "Deep Study Session (60–75 min)",
                "Adequate sleep allows your brain to focus well and absorb information more effectively.",
                "Longer sessions are well suited for complex subjects when you are properly rested."
            ))
        if energy >= 4:
            morning.append(explain_task(
                "Optional Gym / Workout",
                "High energy levels allow you to handle physical activity without it affecting your focus later.",
                "Exercise improves mood, lowers stress, and increases overall concentration throughout the day."
            ))
        else:
            morning.append(explain_task(
                "Light Activity / Rest",
                "Your energy is not high enough to support an intense workout without impacting your performance later.",
                "Saving your energy now helps you stay alert and focused during classes and study time."
            ))
        display_plan_section("Morning", morning)

        if classes:
            display_plan_section("Classes", [
                explain_task(
                    f"Class {i+1} ({s} to {e})",
                    "This is a scheduled class that requires your focus and active participation.",
                    "Short breaks between classes help restore your attention and keep you engaged through the full day."
                ) for i, (s, e) in enumerate(classes)
            ])

    # ---- STUDENT-ATHLETE pre-plan ----
    elif role == "student_athlete":
        morning = []
        morning.append(explain_task(
            "Focused Study Session (30–60 min)",
            "Getting schoolwork done early prevents practice from pushing it out of your schedule later in the day.",
            "Student-athletes have demanding schedules, so handling academics in the morning keeps both areas on track."
        ))
        if energy >= 4:
            morning.append(explain_task(
                "Optional Gym / Pre-Practice Training",
                "Your energy is high enough to handle extra training before practice without showing up already worn down.",
                "Adding a short conditioning session before practice builds fitness over time, as long as the effort is managed well."
            ))
        else:
            morning.append(explain_task(
                "Light Mobility / Rest",
                "Your energy is too low to add more training before practice without risking fatigue going into the session.",
                "Light movement or rest now helps preserve your performance for when it matters most during practice."
            ))
        display_plan_section("Morning", morning)

        if classes:
            display_plan_section("Classes", [
                explain_task(
                    f"Class {i+1} ({s} to {e})",
                    "Keeping up with classes is just as important as keeping up with your athletic commitments.",
                    "Staying focused during class periods helps you manage both school and sports without falling behind."
                ) for i, (s, e) in enumerate(classes)
            ])

        if practice_today == "yes":
            display_plan_section("Practice", [explain_task(
                f"Practice Session ({practice_start} to {practice_end})",
                "Practice is the main driver of athletic improvement and is the most physically demanding part of your day.",
                "Showing up with full effort and focus each session is what drives consistent progress and performance over time."
            )])

    # ---- WORKING ADULT pre-plan ----
    elif role == "adult":
        morning = []
        if sleep < 6:
            morning.append(explain_task(
                "Light Morning Routine / Prep",
                "Low sleep slows your thinking and reduces your ability to concentrate, making a heavy morning routine harder to handle.",
                "A lighter start gives your mind time to wake up gradually without adding more pressure to an already tired state."
            ))
        else:
            morning.append(explain_task(
                "Morning Planning / Routine",
                "Good sleep means your mind is clear and ready, making it a good time to plan and prepare for the day.",
                "A consistent morning routine improves focus, reduces stress, and sets a productive tone before work begins."
            ))
        display_plan_section("Morning", morning)
        display_plan_section("Work Block", [explain_task(
            f"Work ({work_start} to {work_end})",
            "Work is the largest demand on your time and energy today.",
            "Maintaining steady focus and managing your energy during work hours leads to better output and less fatigue afterward."
        )])

    st.divider()

    # ----------------------------------------------------------
    # POST CHECK-IN
    # ----------------------------------------------------------

    if role == "student":
        st.subheader("Step 4 — Post-class check-in")
        st.caption("Your classes are done. How are you feeling right now?")
        pc1, pc2 = st.columns(2)
        post_stress  = pc1.slider("Stress level after classes (1–5)", 1, 5, 3, key="post_stress")
        post_energy  = pc2.slider("Energy level after classes (1–5)", 1, 5, 3, key="post_energy")

        if st.button("Generate rest of my day ▶", type="primary", use_container_width=True):
            st.divider()
            st.subheader("📋 Afternoon & Evening Plan")
            after = []
            if post_stress >= 4 or post_energy <= 2:
                after.append(explain_task(
                    "Recovery + Light Study",
                    "High stress or low energy after classes means your mental capacity is reduced and pushing harder will likely lead to poor results.",
                    "Taking time to recover first restores your focus and makes the study time you do put in much more effective."
                ))
            else:
                after.append(explain_task(
                    "Study / Gym / Productive Work",
                    "Your stress and energy are in a reasonable range, meaning you still have the capacity to be productive.",
                    "This is a good window to study, work out, or handle other tasks while your energy is still available."
                ))
            display_plan_section("After Classes", after)
            display_plan_section("Evening", [explain_task(
                "Review + Planning Session",
                "Evenings are well suited for reviewing what you covered during the day and organizing what is coming up.",
                "Reviewing material helps it stick in your memory, and planning ahead reduces stress going into the next morning."
            )])
            show_insights(role, sleep, stress_before, avg_stress)

    elif role == "student_athlete":
        if practice_today == "yes":
            st.subheader("Step 5 — Post-practice check-in")
            st.caption(f"Practice is done ({practice_start} to {practice_end}). How is your body and mind feeling?")
            pp1, pp2 = st.columns(2)
            post_practice_stress = pp1.slider("Stress level after practice (1–5)", 1, 5, 3, key="pp_stress")
            post_practice_energy = pp2.slider("Energy level after practice (1–5)", 1, 5, 3, key="pp_energy")

            if st.button("Generate rest of my day ▶", type="primary", use_container_width=True):
                st.divider()
                st.subheader("📋 Post-Practice Plan")
                post_practice_tasks = []
                if post_practice_stress >= 4 or post_practice_energy <= 2:
                    post_practice_tasks.append(explain_task(
                        "Recovery / Stretching / Nutrition",
                        "Practice left you physically and mentally drained, and attempting more demanding tasks now will slow down your body's ability to recover.",
                        "Stretching, eating, and resting after a hard practice reduces soreness, lowers injury risk, and puts you in a better state for studying later."
                    ))
                else:
                    post_practice_tasks.append(explain_task(
                        "Light Study or Supplemental Conditioning",
                        "Your post-practice condition is stable enough to take on light tasks without pushing past your limits.",
                        "Staying active or productive after practice at a low intensity keeps the day on track without adding unnecessary strain."
                    ))
                display_plan_section("After Practice", post_practice_tasks)
                evening = [explain_task(
                    "Study + Review Session",
                    "Consistent academic effort in the evening is necessary to prevent schoolwork from falling behind during a demanding athletic schedule.",
                    "Even a focused 30 to 45 minutes of review goes a long way toward staying on top of your courses."
                )]
                if energy >= 3:
                    evening.append(explain_task(
                        "Optional Gym / Supplemental Conditioning",
                        "You have enough energy remaining to support some light additional training if desired.",
                        "Keep the intensity low since you already completed practice today. The goal is to complement your training, not add excess fatigue."
                    ))
                display_plan_section("Evening", evening)
                show_insights(role, sleep, stress_before, avg_stress)

        else:
            st.subheader("Step 5 — Rest of day plan")
            st.caption("No practice today. Here is your full afternoon and evening.")
            if st.button("Generate rest of my day ▶", type="primary", use_container_width=True):
                st.divider()
                st.subheader("📋 Afternoon & Evening Plan")
                evening = [explain_task(
                    "Study + Review Session",
                    "No practice today means more time and energy available for schoolwork. It is worth making the most of it.",
                    "Use the extra availability to catch up on assignments, review material, or prepare for upcoming assessments."
                )]
                if energy >= 3:
                    evening.append(explain_task(
                        "Optional Gym / Conditioning",
                        "Your energy is sufficient for a workout and there is no practice today, making this a good opportunity for extra training.",
                        "A conditioning or skill session on a lighter day supports your development while staying within a manageable workload."
                    ))
                display_plan_section("Evening", evening)
                show_insights(role, sleep, stress_before, avg_stress)

    elif role == "adult":
        st.subheader("Step 4 — Post-work check-in")
        st.caption(f"Work is done ({work_start} to {work_end}). How are you feeling right now?")
        pw1, pw2 = st.columns(2)
        post_work_stress = pw1.slider("Stress level after work (1–5)", 1, 5, 3, key="pw_stress")
        post_work_energy = pw2.slider("Energy level after work (1–5)", 1, 5, 3, key="pw_energy")

        if st.button("Generate rest of my day ▶", type="primary", use_container_width=True):
            st.divider()
            st.subheader("📋 Post-Work Plan")
            after = []
            if post_work_stress >= 4 or post_work_energy <= 2:
                after.append(explain_task(
                    "Recovery / Meditation / Rest",
                    "High stress or low energy after work indicates that your mind and body need recovery before taking on anything else.",
                    "Resting or doing something low-key helps reduce stress, restore your energy, and set you up for a better next day."
                ))
            else:
                if energy >= 3:
                    after.append(explain_task(
                        "Gym / Cardio Workout",
                        "Your energy and stress levels are in a good range to support physical activity after work.",
                        "Working out after work is one of the most effective ways to reduce leftover stress and improve your sleep and mood."
                    ))
                else:
                    after.append(explain_task(
                        "Light Activity / Rest",
                        "Your energy is not high enough for an intense workout, and forcing one in this state tends to do more harm than good.",
                        "Light movement such as a short walk or stretching keeps you active without draining what little energy you have left."
                    ))
            display_plan_section("After Work", after)
            display_plan_section("Evening", [explain_task(
                "Wind Down / Personal Time",
                "The evening should be used to mentally step away from work and decompress.",
                "A consistent wind-down routine improves sleep quality and helps you feel more ready and motivated the next day."
            )])
            show_insights(role, sleep, stress_before, avg_stress)

    st.divider()
    if st.button("↩ Start a new day", use_container_width=True):
        st.session_state.phase = 1
        st.session_state.data = {}
        st.rerun()