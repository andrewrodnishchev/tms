import sqlite3
import logging
from flask import Flask, render_template, request, redirect, url_for, g

main = Flask(__name__)

# Настройка логирования
logging.basicConfig(filename='app.log', level=logging.INFO)

# Подключение к базе данных SQLite
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('projects.db', timeout=10)  # Добавлен параметр timeout
    return db

# Закрытие соединения с базой данных при завершении запроса
@main.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Создание таблицы для хранения проектов, если она не существует
def init_db():
    with main.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", ('projects',))
        table_exists = cursor.fetchone()
        if not table_exists:
            with main.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
            logging.info("Таблица 'projects' создана успешно.")

@main.before_request
def before_first_request_func():
    init_db()

@main.route('/')
def index():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects")
            projects_data = cursor.fetchall()
            projects = [{'id': row[0], 'name': row[1]} for row in projects_data]
            logging.info('Выполнен запрос к базе данных для получения списка проектов')
            logging.debug(f'Получены данные проектов: {projects}')
        return render_template('index.html', projects=projects)
    except sqlite3.Error as e:
        logging.error(f'Ошибка при выполнении SQL-запроса: {e}')
        return "Произошла ошибка при загрузке списка проектов."

@main.route('/project/<int:project_id>')
def project(project_id):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id=?", (project_id,))
            project = cursor.fetchone()
            logging.info(f'Выполнен запрос к базе данных для получения проекта с id={project_id}')
            logging.debug(f'Получен проект: {project}')
        if project is None:
            return "Проект не найден"
        return render_template('project.html', project=project)
    except sqlite3.Error as e:
        logging.error(f'Ошибка при выполнении SQL-запроса: {e}')
        return "Произошла ошибка при загрузке информации о проекте."

@main.route('/add_project', methods=['POST'])
def add_project():
    try:
        name = request.form['name']
        description = request.form.get('description', '')
        date_added = request.form.get('date_added', '')
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO projects (name, description, date_added) VALUES (?, ?, ?)", (name, description, date_added))
            conn.commit()
        logging.info('Проект успешно добавлен в базу данных')
        return redirect(url_for('index'))
    except (KeyError, sqlite3.Error) as e:
        logging.error(f'Ошибка при добавлении проекта: {e}')
        return "Ошибка при добавлении проекта."

@main.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id=?", (project_id,))
            conn.commit()
        logging.info('Проект успешно удален из базы данных')
        return redirect(url_for('index'))
    except sqlite3.Error as e:
        logging.error(f'Ошибка при удалении проекта: {e}')
        return "Ошибка при удалении проекта."

@main.route('/confirm_delete/<int:project_id>', methods=['GET'])
def confirm_delete(project_id):
    return render_template('confirm_delete.html', project_id=project_id)

@main.route('/search_projects', methods=['GET'])
def search_projects():
    query = request.args.get('query')
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE name LIKE ?", ('%' + query + '%',))
            projects_data = cursor.fetchall()
            projects = [{'id': row[0], 'name': row[1]} for row in projects_data]
        return render_template('index.html', projects=projects)
    except sqlite3.Error as e:
        logging.error(f'Ошибка при выполнении SQL-запроса: {e}')
        return "Произошла ошибка при поиске проектов."


if __name__ == '__main__':
    main.run(debug=True)
