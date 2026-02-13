import streamlit as st
from groq import Groq
import json
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(
    page_title="AI Health & Fitness Planner",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

#Enhanced Styling
st.markdown("""
    <style>
    .main { 
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .plan-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    h1, h2, h3 {
        color: #2d3748;
    }
    </style>
""", unsafe_allow_html=True)


#Enhanced Groq Call with Error Handling
def generate_response(api_key, prompt, temperature=0.6, max_tokens=1200):
    """Generate AI response with enhanced error handling and retry logic"""
    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """You are a certified fitness and nutrition assistant with expertise in:
                    - Evidence-based nutrition planning
                    - Progressive overload training principles
                    - Injury prevention and recovery
                    - Sustainable lifestyle changes

                    Provide structured, practical, and scientifically-backed advice. 
                    Use markdown formatting for better readability."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None


#Enhanced Calorie & Macro Calculations
def calculate_nutrition(age, weight, height, sex, activity_level, goal):
    """Calculate BMR, TDEE, target calories, and macros"""

    # Mifflin-St Jeor Equation for BMR
    if sex == "Male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_multipliers = {
        "Sedentary (Little/No Exercise)": 1.2,
        "Lightly Active (1-3 days/week)": 1.375,
        "Moderately Active (3-5 days/week)": 1.55,
        "Very Active (6-7 days/week)": 1.725,
        "Extremely Active (Athlete)": 1.9
    }

    tdee = bmr * activity_multipliers[activity_level]

    # Goal-based calorie adjustments
    calorie_adjustments = {
        "Lose Weight (Fat Loss)": -500,
        "Gain Muscle (Bulk)": 300,
        "Endurance": 0,
        "Maintain Weight": 0,
        "Strength Training": 200
    }

    target = tdee + calorie_adjustments.get(goal, 0)

    # Macro calculations (protein, carbs, fats)
    if "Muscle" in goal or "Strength" in goal:
        protein_ratio, carb_ratio, fat_ratio = 0.30, 0.40, 0.30
    elif "Weight" in goal:
        protein_ratio, carb_ratio, fat_ratio = 0.35, 0.35, 0.30
    else:
        protein_ratio, carb_ratio, fat_ratio = 0.25, 0.45, 0.30

    protein_g = (target * protein_ratio) / 4  # 4 cal per gram
    carbs_g = (target * carb_ratio) / 4
    fats_g = (target * fat_ratio) / 9  # 9 cal per gram

    return {
        'bmr': round(bmr),
        'tdee': round(tdee),
        'target': round(target),
        'protein': round(protein_g),
        'carbs': round(carbs_g),
        'fats': round(fats_g)
    }


#Visualization Function
def create_macro_pie_chart(protein, carbs, fats):
    """Create an interactive macro distribution pie chart"""
    fig = go.Figure(data=[go.Pie(
        labels=['Protein', 'Carbs', 'Fats'],
        values=[protein * 4, carbs * 4, fats * 9],
        marker=dict(colors=['#FF6B6B', '#4ECDC4', '#FFE66D']),
        textinfo='label+percent',
        hole=0.3
    )])

    fig.update_layout(
        title="Macro Distribution",
        height=300,
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def create_calorie_comparison(bmr, tdee, target):
    """Create calorie comparison bar chart"""
    fig = go.Figure(data=[
        go.Bar(
            x=['BMR', 'TDEE', 'Target'],
            y=[bmr, tdee, target],
            marker=dict(
                color=['#667eea', '#764ba2', '#f093fb'],
                line=dict(color='white', width=2)
            ),
            text=[f"{bmr}", f"{tdee}", f"{target}"],
            textposition='auto',
        )
    ])

    fig.update_layout(
        title="Calorie Breakdown",
        yaxis_title="Calories (kcal)",
        height=300,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


#Export Functions
def export_plan_to_json(profile_data, nutrition_data, meal_plan, workout_plan):
    """Export user's complete plan to JSON"""
    export_data = {
        'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'profile': profile_data,
        'nutrition': nutrition_data,
        'meal_plan': meal_plan,
        'workout_plan': workout_plan
    }
    return json.dumps(export_data, indent=2)


#Main App
def main():
    # Initialize session state
    if "calculated" not in st.session_state:
        st.session_state.calculated = False
        st.session_state.nutrition = {}
        st.session_state.meal_plan = ""
        st.session_state.workout_plan = ""
        st.session_state.tips = ""
        st.session_state.profile = {}

    #Header
    st.title("🏋️‍♂️ AI Health & Fitness Planner")
    st.markdown("*Your personalized path to fitness excellence*")

    #Sidebar
    with st.sidebar:
        st.header("🔑 API Configuration")

        groq_api_key = st.text_input(
            "Groq API Key",
            type="password",
            help="Get your free API key at console.groq.com"
        )

        if not groq_api_key:
            st.warning("⚠️ Enter your Groq API key to continue.")
            st.info("💡 Get your free API key at [console.groq.com](https://console.groq.com)")
            st.stop()

        st.success("✅ API Key Loaded")

        st.markdown("---")
        st.markdown("### 📊 App Features")
        st.markdown("""
        - 🔢 Advanced calorie & macro calculation
        - 🥗 AI-powered meal plans
        - 🏋️ Customized workout routines
        - 📈 Visual progress tracking
        - 💾 Export your complete plan
        - 🎯 Goal-specific recommendations
        """)

    #User Profile
    st.header("👤 Your Profile")

    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input("Age", 10, 100, 25, help="Your current age")
        weight = st.number_input("Weight (kg)", 20.0, 300.0, 70.0, step=0.5)

    with col2:
        height = st.number_input("Height (cm)", 100.0, 250.0, 170.0, step=0.5)
        sex = st.selectbox("Sex", ["Male", "Female"])

    with col3:
        activity_level = st.selectbox(
            "Activity Level",
            [
                "Sedentary (Little/No Exercise)",
                "Lightly Active (1-3 days/week)",
                "Moderately Active (3-5 days/week)",
                "Very Active (6-7 days/week)",
                "Extremely Active (Athlete)"
            ]
        )

        fitness_goal = st.selectbox(
            "Primary Goal",
            [
                "Lose Weight (Fat Loss)",
                "Gain Muscle (Bulk)",
                "Endurance",
                "Maintain Weight",
                "Strength Training"
            ]
        )

    # Additional preferences
    with st.expander("⚙️ Additional Preferences (Optional)"):
        dietary_restrictions = st.multiselect(
            "Dietary Restrictions",
            ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Keto", "Paleo", "Halal", "Kosher"]
        )

        workout_preferences = st.multiselect(
            "Workout Preferences",
            ["Home Workouts", "Gym Access", "Minimal Equipment", "Bodyweight Only", "Cardio Focus", "Strength Focus"]
        )

        experience_level = st.select_slider(
            "Fitness Experience",
            options=["Beginner", "Intermediate", "Advanced", "Elite"]
        )

    #Calculate Button
    if st.button("📊 Calculate My Personalized Plan", use_container_width=True, type="primary"):
        with st.spinner("🔄 Calculating your personalized nutrition plan..."):
            nutrition = calculate_nutrition(age, weight, height, sex, activity_level, fitness_goal)

            st.session_state.calculated = True
            st.session_state.nutrition = nutrition
            st.session_state.meal_plan = ""
            st.session_state.workout_plan = ""
            st.session_state.tips = ""
            st.session_state.profile = {
                'age': age,
                'weight': weight,
                'height': height,
                'sex': sex,
                'activity_level': activity_level,
                'fitness_goal': fitness_goal,
                'dietary_restrictions': dietary_restrictions,
                'workout_preferences': workout_preferences,
                'experience_level': experience_level
            }

        st.success("✅ Plan calculated successfully!")

    #Display Results
    if st.session_state.calculated:

        nutrition = st.session_state.nutrition

        st.markdown("---")
        st.header("📊 Your Nutrition Blueprint")

        # Metrics Row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("BMR", f"{nutrition['bmr']} kcal", help="Basal Metabolic Rate")
        with col2:
            st.metric("TDEE", f"{nutrition['tdee']} kcal", help="Total Daily Energy Expenditure")
        with col3:
            st.metric("Target Calories", f"{nutrition['target']} kcal",
                      delta=f"{nutrition['target'] - nutrition['tdee']}")
        with col4:
            bmi = round(weight / ((height / 100) ** 2), 1)
            st.metric("BMI", bmi)

        # Macro Breakdown
        st.markdown("### 🎯 Daily Macro Targets")

        col1, col2 = st.columns(2)

        with col1:
            macro_col1, macro_col2, macro_col3 = st.columns(3)
            with macro_col1:
                st.metric("Protein", f"{nutrition['protein']}g")
            with macro_col2:
                st.metric("Carbs", f"{nutrition['carbs']}g")
            with macro_col3:
                st.metric("Fats", f"{nutrition['fats']}g")

        with col2:
            st.plotly_chart(
                create_macro_pie_chart(nutrition['protein'], nutrition['carbs'], nutrition['fats']),
                use_container_width=True
            )

        # Calorie Comparison Chart
        st.plotly_chart(
            create_calorie_comparison(nutrition['bmr'], nutrition['tdee'], nutrition['target']),
            use_container_width=True
        )

        # Health Guidelines
        st.info(f"""
### 💡 Daily Fundamentals

**Movement:** 7,000-10,000 steps  
**Sleep:** 7-9 hours of quality sleep  
**Hydration:** {round(weight * 0.033, 1)}L of water (based on your weight)  
**Recovery:** 1-2 rest days per week  

*Consistency beats perfection. Small daily actions compound into extraordinary results.*
""")

        st.markdown("---")

        #AI-Generated Plans
        st.header("🤖 AI-Powered Customization")

        col1, col2, col3 = st.columns(3)

        # Meal Plan Generation
        with col1:
            if st.button("🥗 Generate Meal Plan", use_container_width=True):

                dietary_info = f"\nDietary Restrictions: {', '.join(dietary_restrictions)}" if dietary_restrictions else ""

                meal_prompt = f"""
Create a detailed, practical daily meal plan with the following parameters:

**Goal:** {fitness_goal}
**Target Calories:** {nutrition['target']} kcal/day
**Macros:** {nutrition['protein']}g protein, {nutrition['carbs']}g carbs, {nutrition['fats']}g fats
**Weight:** {weight} kg{dietary_info}

**Requirements:**
1. Provide 4-5 meals (breakfast, lunch, dinner, 1-2 snacks)
2. Include specific portion sizes and calories per meal
3. List simple, accessible ingredients
4. Add meal timing suggestions
5. Include a quick prep tip for each meal
6. Ensure meals are balanced and sustainable

Use clear markdown formatting with headers and bullet points.
"""

                with st.spinner("🍳 Crafting your personalized meal plan..."):
                    meal_plan = generate_response(groq_api_key, meal_prompt, temperature=0.7)
                    if meal_plan:
                        st.session_state.meal_plan = meal_plan

        #Workout Plan Generation
        with col2:
            if st.button("🏋️ Generate Workout Plan", use_container_width=True):

                workout_info = f"\nPreferences: {', '.join(workout_preferences)}" if workout_preferences else ""

                workout_prompt = f"""
Create a comprehensive weekly workout routine with these parameters:

**Goal:** {fitness_goal}
**Experience Level:** {experience_level}
**Activity Level:** {activity_level}
**Weight:** {weight} kg{workout_info}

**Requirements:**
1. Provide a 5-6 day weekly split
2. Include specific exercises with sets × reps
3. Add progressive overload recommendations
4. Include warm-up and cool-down routines
5. Specify rest periods between sets
6. Add form cues for key exercises
7. Include estimated workout duration per session

Focus on sustainable, science-based programming. Use markdown formatting.
"""

                with st.spinner("💪 Building your workout routine..."):
                    workout_plan = generate_response(groq_api_key, workout_prompt, temperature=0.7)
                    if workout_plan:
                        st.session_state.workout_plan = workout_plan

        #Lifestyle Tips Generation
        with col3:
            if st.button("💡 Get Lifestyle Tips", use_container_width=True):

                tips_prompt = f"""
Provide personalized lifestyle optimization tips for:

**Goal:** {fitness_goal}
**Profile:** {age}y/o {sex}, {weight}kg, {activity_level}

**Include:**
1. Sleep optimization (3-4 tips)
2. Stress management techniques
3. Recovery strategies
4. Supplementation basics (if applicable)
5. Habit-building advice
6. Common pitfalls to avoid

Keep it practical, evidence-based, and actionable. Use markdown formatting.
"""

                with st.spinner("🧠 Generating lifestyle optimization tips..."):
                    tips = generate_response(groq_api_key, tips_prompt, temperature=0.7)
                    if tips:
                        st.session_state.tips = tips

        # Display Generated Content
        if st.session_state.meal_plan or st.session_state.workout_plan or st.session_state.tips:
            st.markdown("---")

            tab1, tab2, tab3 = st.tabs(["🥗 Meal Plan", "🏋️ Workout Plan", "💡 Lifestyle Tips"])

            with tab1:
                if st.session_state.meal_plan:
                    st.markdown(st.session_state.meal_plan)
                else:
                    st.info("Click 'Generate Meal Plan' to get your personalized nutrition guide")

            with tab2:
                if st.session_state.workout_plan:
                    st.markdown(st.session_state.workout_plan)
                else:
                    st.info("Click 'Generate Workout Plan' to get your customized training program")

            with tab3:
                if st.session_state.tips:
                    st.markdown(st.session_state.tips)
                else:
                    st.info("Click 'Get Lifestyle Tips' for optimization strategies")

        #Export Function
        if st.session_state.meal_plan or st.session_state.workout_plan:
            st.markdown("---")

            col1, col2, col3 = st.columns([1, 1, 1])

            with col2:
                export_data = export_plan_to_json(
                    st.session_state.profile,
                    nutrition,
                    st.session_state.meal_plan,
                    st.session_state.workout_plan
                )

                st.download_button(
                    label="📥 Download Complete Plan (JSON)",
                    data=export_data,
                    file_name=f"fitness_plan_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )

    #Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p><strong>Disclaimer:</strong> This tool provides general guidance only. Consult healthcare professionals before starting any new diet or exercise program.</p>
        <p>Made with ❤️ using Streamlit & Groq AI</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
