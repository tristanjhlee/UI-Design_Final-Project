from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)

# Quiz 

@app.route('/')
def home():
    session.clear()
    return render_template('index.html')

@app.route('/learn/<int:lesson_num>')
def learn(lesson_num):
    with open('data/learn.json') as f:
        lessons = json.load(f)
    lesson = next((l for l in lessons if l["lesson_num"] == lesson_num), None)
    if not lesson:
        return "Lesson not found", 404
    return render_template("learn.html", lesson=lesson)


@app.route('/quiz/<int:quiz_num>', methods=['GET'])
def quiz(quiz_num):
    with open('data/quiz.json') as f:
        quizzes = json.load(f)

    quiz_data = next((q for q in quizzes if q["quiz_num"] == quiz_num), None)
    if not quiz_data:
        return "Quiz not found", 404

    quiz_type = quiz_data["type"]
    if quiz_type == "drag_match":
        return render_template("quiz_drag.html", question=quiz_data, question_num=quiz_num)
    elif quiz_type == "dropdown":
        return render_template("quiz_dropdown.html", question=quiz_data, question_num=quiz_num)
    elif quiz_type == "table_drag_match":
        return render_template("quiz_table.html", question=quiz_data, question_num=quiz_num)
    elif quiz_type == "connect_line":
        return render_template("quiz_connect.html", question=quiz_data, question_num=quiz_num)
    elif quiz_type == "design_choice":
        return render_template("quiz_select.html", question=quiz_data, question_num=quiz_num)
    else:
        return "Unsupported quiz type", 400

# Quiz Submit

@app.route('/submit_quiz/<int:quiz_num>', methods=['POST'])
def submit_quiz(quiz_num):
    with open('data/quiz.json') as f:
        quizzes = json.load(f)

    quiz_data = next((q for q in quizzes if q["quiz_num"] == quiz_num), None)
    if not quiz_data:
        return "Quiz not found", 404

    quiz_type = quiz_data["type"]

    # Quiz 1: Drag & Drop
    if quiz_type == "drag_match":
        user_matches_raw = request.form.get('matchResult')
        if not user_matches_raw:
            return "Missing matchResult", 400
        user_matches = json.loads(user_matches_raw)
        correct = dict(zip(quiz_data["correct"], quiz_data["descriptions"]))
        score = 0
        for topic, desc in user_matches.items():
            if topic in correct and correct[topic] == desc:
                score += 1
        session['score'] = score
        session['total'] = len(correct)
        return redirect(url_for('result'))

    # Quiz 2: Dropdown
    elif quiz_type == "dropdown":
        driving_env = request.form.get('driving_env')
        riders = request.form.get('riders')
        recommendation = quiz_data["rules"].get(driving_env, {}).get(riders, "Unknown")
        session['car_recommendation'] = recommendation
        return redirect(url_for('result2'))

    # Quiz 3: Fuel Table Drag & Drop
    elif quiz_type == "table_drag_match":
        user_matches_raw = request.form.get('matchResult')
        if not user_matches_raw:
            return "Missing matchResult", 400
        user_matches = json.loads(user_matches_raw)
        correct = quiz_data["correct_order"]
        score = 0
        for idx, fuel in user_matches.items():
            if correct.get(idx) == fuel:
                score += 1
        session['quiz3_score'] = score
        return redirect(url_for('result3'))
        
    # Quiz 4: Safety Features
    elif quiz_type == "connect_line":
        user_matches_raw = request.form.get('matchResult')
        if not user_matches_raw:
            return "Missing matchResult", 400
        user_matches = json.loads(user_matches_raw)
        correct = quiz_data["correct"]
        score = 0
        for key, value in correct.items():
            if key in user_matches and user_matches[key] == value:
                score += 1
        session['score'] = score
        session['total'] = len(correct)
        return redirect(url_for('result4'))
    
    # Quiz 5: Design & Interior
    elif quiz_type == "design_choice":
        selected = request.form.get('style_choice')
        option = next((o for o in quiz_data["options"] if o["label"] == selected), None)
        if not option:
            return "Invalid selection", 400
        session['selected_brands'] = option["brands"]
        session['selected_images'] = option["images"]
        return redirect(url_for('result5'))

    return "Unsupported submission type", 400

# Result

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/result2')
def result2():
    return render_template('result2.html', recommendation=session.get('car_recommendation'))

@app.route('/result3')
def result3():
    return render_template('result3.html', score=session.get('quiz3_score', 0))

@app.route('/result4')
def result4():
    return render_template('result4.html', score=session.get('score'), total=session.get('total'))

@app.route('/result5')
def result5():
    return render_template('result5.html', brands=session.get('selected_brands'), images=session.get('selected_images', []))

@app.route('/log-page-enter', methods=['POST'])
def log_page_enter():
    print("Page enter log:", request.json)
    return '', 204

if __name__ == '__main__':
    app.run(port=5001, debug=True)
