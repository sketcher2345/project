from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'abcd44'

# MySQL Connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="bibek",
    database="question"
)
ques = mydb.cursor()

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_test', methods=['POST'])
def start_test():
    delete_table = request.form.get('delete_questions')
    if delete_table == "yes":
        cmdo = "DROP TABLE IF EXISTS q_paper"  # deletion if exists
        ques.execute(cmdo)
        mydb.commit()
        return redirect(url_for('set_question_paper'))
    else:
        return redirect(url_for('test'))

@app.route('/set_question_paper', methods=['GET', 'POST'])
def set_question_paper():
    num_questions = 5  # Default value for num_questions
    if request.method == 'POST':
        try:
            # Extract num_questions from the form data
            num_questions = int(request.form.get('num_questions'))
            questions = []
            for i in range(num_questions):
                # Extract question, options, and correct_option for each question from the form data
                question = request.form.get('question_' + str(i + 1))
                options = [request.form.get('option_' + str(i + 1) + '_' + str(j)) for j in range(1, 5)]
                correct_option = request.form.get('correct_option_' + str(i + 1))
                questions.append((question, *options, correct_option))  # Include all options in a tuple

            # Save questions to the database
            cmd = "DROP TABLE IF EXISTS q_paper"  # Drop the existing table
            ques.execute(cmd)
            cmd = "CREATE TABLE q_paper(No INT AUTO_INCREMENT PRIMARY KEY, quest VARCHAR(250) NOT NULL, opt1 VARCHAR(250) NOT NULL, opt2 VARCHAR(250) NOT NULL, opt3 VARCHAR(250) NOT NULL, opt4 VARCHAR(250) NOT NULL, correct_option VARCHAR(10))"
            ques.execute(cmd)
            for q in questions:
                cmd2 = "INSERT INTO q_paper(quest, opt1, opt2, opt3, opt4, correct_option) VALUES(%s, %s, %s, %s, %s, %s)"
                ques.execute(cmd2, q)
            mydb.commit()
            flash('Questions submitted successfully!', 'success')
            return redirect(url_for('test'))  # Redirect to the test route after successful submission
        except Exception as e:
            flash('An error occurred while submitting questions.', 'error')
            # Log the error for debugging purposes
            print("Error:", e)
            mydb.rollback()

    return render_template('set_question_paper.html', num_questions=num_questions)




@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        # Process test submission
        score = 0
        num_questions = int(request.form.get('num_questions'))
        for i in range(1, num_questions + 1):
            user_answer = request.form.get('answer_' + str(i))
            correct_option = request.form.get('correct_option_' + str(i))

            # Fetch the correct option from the database for the current question
            cmd = "SELECT correct_option FROM q_paper WHERE No = %s"
            ques.execute(cmd, (i,))
            correct_option_db = ques.fetchone()[0]

            # Compare user's response with the correct option from the database
            if user_answer.strip().lower() == correct_option_db.strip().lower():
                score += 1

        # Save or display the score
        student_name = request.form.get('student_name')
        flash('Test submitted successfully!', 'success')
        return redirect(url_for('result', student_name=student_name, score=score))  # Redirect to result route

    else:
        # Fetch questions from the database
        cmd = "SELECT * FROM q_paper"
        ques.execute(cmd)
        questions = ques.fetchall()
        num_questions = len(questions)

        return render_template('test.html', questions=questions, num_questions=num_questions)



@app.route('/result')
def result():
    # Fetch the student name and score from the request arguments
    student_name = request.args.get('student_name')
    score = request.args.get('score')

    # Insert the student's name and score into the 'marks' table
    cur = mydb.cursor()
    cmd = "INSERT INTO marks (StudentName, Marks) VALUES (%s, %s)"
    cur.execute(cmd, (student_name, score))
    mydb.commit()

    # Retrieve all entries from the 'marks' table and display them in descending order of marks
    cmd = "SELECT * FROM marks ORDER BY Marks DESC"
    cur.execute(cmd)
    data = cur.fetchall()

    return render_template('result.html', data=data)

    
@app.route('/thanks')
def thanks():
    return render_template('thanks.html')


if __name__ == '__main__':
    app.run(debug=True)
