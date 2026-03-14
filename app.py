from flask import Flask, render_template, request, jsonify
from questions_data import QUESTIONS, SKILL_ALIASES, COMPANIES, SKILL_DISPLAY_NAMES, SKILL_ICONS

app = Flask(__name__)

def resolve_skill(skill_input):
    skill = skill_input.strip().lower()
    skill = SKILL_ALIASES.get(skill, skill)
    return skill if skill in QUESTIONS else None

@app.route("/")
def index():
    skills = list(QUESTIONS.keys())
    return render_template("index.html", skills=skills, display_names=SKILL_DISPLAY_NAMES, icons=SKILL_ICONS)

@app.route("/api/questions", methods=["POST"])
def get_questions():
    data = request.get_json()
    skill_input = data.get("skill", "").strip()
    companies = data.get("companies", COMPANIES)

    skill = resolve_skill(skill_input)
    if not skill:
        # fuzzy match
        for key in QUESTIONS:
            if skill_input.lower() in key or key in skill_input.lower():
                skill = key
                break

    if not skill:
        return jsonify({"error": f"No questions found for skill: '{skill_input}'. Try: Python, SQL, Machine Learning, Data Science, Data Analysis, Data Engineering, Behavioral, General Technical"}), 404

    result = {}
    for company in companies:
        if company in QUESTIONS[skill]:
            result[company] = QUESTIONS[skill][company]

    return jsonify({
        "skill": skill,
        "display_name": SKILL_DISPLAY_NAMES.get(skill, skill.title()),
        "icon": SKILL_ICONS.get(skill, "📌"),
        "companies": result,
        "total": sum(len(v) for v in result.values())
    })

@app.route("/api/skills")
def get_skills():
    return jsonify({
        "skills": [
            {"key": k, "name": SKILL_DISPLAY_NAMES[k], "icon": SKILL_ICONS[k], "companies": list(QUESTIONS[k].keys())}
            for k in QUESTIONS
        ]
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
