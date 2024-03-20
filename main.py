from flask import Flask, render_template, request, redirect, url_for
from werkzeug.exceptions import BadRequestKeyError

app = Flask(__name__)

# Пример данных с проектами (можно заменить на вашу базу данных)
projects = [
    {'id': 1, 'name': 'Проект А', 'description': 'Описание проекта А', 'date_added': '2024-03-19'},
    {'id': 2, 'name': 'Проект Б', 'description': 'Описание проекта Б', 'date_added': '2024-03-18'},
    {'id': 3, 'name': 'Проект В', 'description': 'Описание проекта В', 'date_added': '2024-03-17'},
    # Добавьте свои проекты сюда
]

@app.route('/')
def index():
    return render_template('index.html', projects=projects)

@app.route('/project/<int:project_id>')
def project(project_id):
    project = next((p for p in projects if p['id'] == project_id), None)
    if project is None:
        return "Проект не найден"
    return render_template('project.html', project=project)

@app.route('/add_project', methods=['POST'])
def add_project():
    try:
        name = request.form['name']
        description = request.form.get('description', '')
        date_added = request.form.get('date_added', '')
        # Генерируем уникальный ID для нового проекта
        new_project_id = max(p['id'] for p in projects) + 1 if projects else 1
        # Добавляем новый проект в список
        projects.append({'id': new_project_id, 'name': name, 'description': description, 'date_added': date_added})
        return redirect(url_for('index'))
    except BadRequestKeyError as e:
        return f"Ошибка при добавлении проекта: {e}"

if __name__ == '__main__':
    app.run(debug=True)
