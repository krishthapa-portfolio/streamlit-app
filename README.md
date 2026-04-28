## 📌 What It Does  

DayCraft is a personalized daily routine system that generates adaptive schedules based on a user’s:

- Role (Student, Student-Athlete, Working Adult)
- Sleep duration
- Energy level
- Stress level
- Post-activity feedback (after class/work/practice)

Unlike a static planner, DayCraft continuously adjusts the rest of the day after checking in with how the user actually feels after their main activity.

---

## 🧠 Core Recommendation Logic (Colab Prototype)

This is the original backend logic built in Google Colab before being moved into Streamlit.

It uses:
- Role-based historical data
- Simple statistical analysis
- Rule-based decision making
- Post-activity feedback loops

```python
# Historical data stored as Pandas DataFrames, one per role
student_history = pd.DataFrame({
    "study_sessions": [2,3,2,4,3,2],
    "gym_sessions":   [1,0,1,1,0,1],
    "focus_success":  [0.7,0.8,0.6,0.85,0.75,0.7],
    "stress":         [3,4,3,5,2,3]
})

# Average stress from past days is used to trigger insights
avg_stress = student_history["stress"].mean()

# Every recommendation comes with a reason and context
def explain_task(task, reason, context):
    return f"- {task}\n  Reason: {reason}\n  Context: {context}\n"

# Recommendations adapt based on sleep, energy, and post-activity feedback
if sleep < 6:
    print(explain_task(
        "Light Focus Study (30-45 min)",
        "Low sleep reduces cognitive endurance and focus capacity.",
        "Short sessions help maintain productivity without mental fatigue accumulation."
    ))
else:
    print(explain_task(
        "Deep Study Session (60-75 min)",
        "Adequate rest supports sustained attention and memory retention.",
        "Longer sessions are effective for complex subjects and assignments."
    ))

# Post-activity check-in. User types stress/energy after classes or work.
post_stress = int(input("Stress level after classes (1-5): "))
post_energy = int(input("Energy level after classes (1-5): "))

if post_stress >= 4 or post_energy <= 2:
    print(explain_task("Recovery + Light Study", ...))
else:
    print(explain_task("Study / Gym / Productive Work", ...))
🔄 How It Was Built

We first built the system entirely in Google Colab as a terminal-based program.

That version handled:

All logic and decision rules
DataFrames for each role
Recommendation engine
Stress and energy-based adaptation

After validating the logic, we migrated everything into Streamlit for a user interface.

🌐 Streamlit Conversion
What Stayed the Same
All Pandas DataFrames (role-based history)
All if/elif recommendation logic
avg_stress calculation
explain_task function logic
What Changed
input() → st.slider(), st.radio(), st.number_input()
print() → st.info(), st.expander()
String output → structured UI components
Added st.session_state for multi-step interaction flow
🧩 Session State Explanation

The biggest structural change was adapting to Streamlit’s rerun system.

In Colab:

input() pauses execution until user responds

In Streamlit:

The entire script reruns every interaction

To handle this, we used:

st.session_state to store user inputs
A phase variable to control app flow (input phase → recommendation phase)

This allows the app to behave like a step-by-step system instead of resetting every interaction.

🤖 On AI Use
AI was used to assist with Streamlit syntax (especially session state and UI structure)
All core logic (recommendation system, rules, DataFrames, decision flow) was designed and written by us in Colab
The final system logic is identical between Colab and app.py

You can verify this by comparing both versions directly.

▶️ Run Locally
pip install streamlit pandas
streamlit run app.py

Or simply use the live link above — no setup required.

## Run It Locally  

```bash
pip install streamlit pandas
streamlit run app.py
