from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

from werkzeug.exceptions import BadRequestKeyError

app = Flask(__name__)

# Подключение к базе данных SQLite
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('projects.db')
    return db

# Закрытие соединения с базой данных при завершении запроса
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Создание таблицы для хранения проектов, если она не существует
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_first_request
def before_first_request_func():
    init_db()

@app.route('/')
def index():
    # Получение списка проектов из базы данных
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()
    return render_template('index.html', projects=projects)

@app.route('/project/<int:project_id>')
def project(project_id):
    # Получение информации о проекте с указанным ID из базы данных
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM projects WHERE id=?", (project_id,))
    project = cursor.fetchone()
    if project is None:
        return "Проект не найден"
    return render_template('project.html', project=project)

@app.route('/add_project', methods=['POST'])
def add_project():
    try:
        # Получение данных о проекте из запроса
        name = request.form['name']
        description = request.form.get('description', '')
        date_added = request.form.get('date_added', '')
        # Добавление нового проекта в базу данных
        cursor = get_db().cursor()
        cursor.execute("INSERT INTO projects (name, description, date_added) VALUES (?, ?, ?)", (name, description, date_added))
        get_db().commit()  # Сохранение изменений
        return redirect(url_for('index'))
    except BadRequestKeyError as e:
        return f"Ошибка при добавлении проекта: {e}"

if __name__ == '__main__':
    app.run(debug=True)
