import os
import csv

# caminho da pasta atual
current_path = os.path.dirname(os.path.abspath(__file__))

# caminho da pasta raiz
main_path = os.path.dirname(current_path)

# pasta db
db_path = os.path.join(main_path, "db")

# cria a pasta db se não existir
if not os.path.exists(db_path):
    os.makedirs(db_path)

# caminhos individuais
USERS = os.path.join(db_path, "users.csv")
PROJECTS = os.path.join(db_path, "projects.csv")
LISTS = os.path.join(db_path, "lists.csv")
TASKS = os.path.join(db_path, "tasks.csv")
COMMENTS = os.path.join(db_path, "comments.csv")

# fieldnames
USER_FIELDNAMES = ['user_id', 'name', 'email', 'password_hash', 'created_at']
PROJECT_FIELDNAMES = ['project_id', 'user_id', 'project_title', 'project_description', 'created_at']
LIST_FIELDNAMES = ['list_id', 'project_id', 'list_name', 'created_at']
TASKS_FIELDNAMES = ['task_id', 'title', 'description', 'completed', 'created_at', 'list_id']
COMMENTS_FIELDNAMES =['comment_id','task_id','content','created_at']


# funcoes gerais de manipulação de CSV

def save_csv(arq, fieldnames, data):
    with open(arq, "a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if os.path.getsize(arq) == 0:
            writer.writeheader()

        writer.writerow(data)


def overwrite_csv(arq, fieldnames, data_list):
    with open(arq, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_list)


def read_csv(arq):
    try:
        with open(arq, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return list(reader)
    except Exception:
        return []


# usuarios

def save_user(user):
    save_csv(USERS, USER_FIELDNAMES, user)


def find_user_by_email(email):
    users = read_csv(USERS)
    for user in users:
        if user.get("email") == email:
            return user
    return None


def find_user_by_id(user_id):
    target_id = str(user_id)
    users = read_csv(USERS)
    for user in users:
        if user.get("user_id") == target_id:
            return user
    return None


def get_next_user_id():
    users = read_csv(USERS)
    if not users:
        return '1'
    max_id = max(int(u.get("user_id", 0)) for u in users)
    return str(max_id + 1)


def update_user_data(user_id, new_data):
    target_id = str(user_id)
    users = read_csv(USERS)
    updated = []
    updated_user = None
    for user in users:
        if user.get("user_id") == target_id:
            user.update(new_data)
            updated_user = user
        updated.append(user)

    overwrite_csv(USERS, USER_FIELDNAMES, updated)

    return updated_user


def delete_user_data(user_id):
    target_user_id = str(user_id)
    
    all_projects = read_csv(PROJECTS)
    for p in all_projects:
        if str(p.get('user_id')) == target_user_id:
            delete_project_data(p['project_id'])

    users = read_csv(USERS)
    remaining_users = [u for u in users if str(u.get("user_id")) != target_user_id]
    overwrite_csv(USERS, USER_FIELDNAMES, remaining_users)


# projetos

def save_project(project):
    save_csv(PROJECTS, PROJECT_FIELDNAMES, project)


def get_next_project_id():
    projects = read_csv(PROJECTS)
    if not projects:
        return '1'
    max_id = max(int(p.get("project_id", 0)) for p in projects)
    return str(max_id + 1)


def find_project_by_id(project_id):
    target_id = str(project_id)
    projects = read_csv(PROJECTS)
    for project in projects:
        if project.get("project_id") == target_id:
            return project
    return None


def find_projects_by_user_id(user_id):
    target_user_id = str(user_id)
    projects = read_csv(PROJECTS)
    user = find_user_by_id(user_id)

    my_projects = []
    for project in projects:
        if project.get("user_id") == target_user_id:
            project.pop("user_id")
            project["owner_user"] = user["name"]
            my_projects.append(project)

    return my_projects


def update_project_data(project_id, new_data):
    target_id = str(project_id)
    projects = read_csv(PROJECTS)
    updated = []

    for project in projects:
        if project.get("project_id") == target_id:
            project.update(new_data)
        updated.append(project)

    overwrite_csv(PROJECTS, PROJECT_FIELDNAMES, updated)

def delete_project_data(project_id):
    target_proj_id = str(project_id)
    all_lists = read_csv(LISTS)

    lists_to_remove = [l for l in all_lists if str(l.get('project_id')) == target_proj_id]
    
    for lista in lists_to_remove:
        delete_list_data(lista['list_id'])

    projects = read_csv(PROJECTS)
    remaining_projects = [p for p in projects if str(p.get("project_id")) != target_proj_id]
    overwrite_csv(PROJECTS, PROJECT_FIELDNAMES, remaining_projects)


# listas

def get_next_list_id():
    lists_data = read_csv(LISTS)
    if not lists_data:
        return '1'
    max_id = max(int(l.get("list_id", 0)) for l in lists_data)
    return str(max_id + 1)

def save_list(lista):
    save_csv(LISTS, LIST_FIELDNAMES, lista)


def find_lists_by_project_id(project_id):
    target_id = str(project_id)
    lists_data = read_csv(LISTS)
    return [l for l in lists_data if l.get("project_id") == target_id]


def find_list_by_id(list_id):
    target_id = str(list_id)
    lists_data = read_csv(LISTS)
    for lista in lists_data:
        if lista.get("list_id") == target_id:
            return lista
    return None


def update_list_data(list_id, new_data):
    target_id = str(list_id)
    lists_data = read_csv(LISTS)
    updated = []

    for lista in lists_data:
        if lista.get("list_id") == target_id:
            lista.update(new_data)
        updated.append(lista)

    overwrite_csv(LISTS, LIST_FIELDNAMES, updated)

def delete_list_data(list_id):
    target_list_id = str(list_id)
    all_tasks = read_csv(TASKS)
    
    tasks_in_list = [t for t in all_tasks if str(t.get('list_id')) == target_list_id]
    
    for task in tasks_in_list:
        delete_task_data(task['task_id'])

    lists_data = read_csv(LISTS)
    remaining_lists = [l for l in lists_data if str(l.get("list_id")) != target_list_id]
    overwrite_csv(LISTS, LIST_FIELDNAMES, remaining_lists)


# tarefas

def get_next_task_id():
    tasks = read_csv(TASKS)
    if not tasks:
        return '1'
    max_id = max(int(t.get("task_id",0)) for t in tasks)

    return str(max_id + 1)


def save_task(task):
    save_csv(TASKS, TASKS_FIELDNAMES, task)


def find_tasks_by_list_id(list_id):
    target_id = str(list_id)
    tasks = read_csv(TASKS)
    return [t for t in tasks if t.get("list_id") == target_id]


def find_task_by_id(task_id):
    target_id = str(task_id)
    tasks = read_csv(TASKS)
    for task in tasks:
        if task.get("task_id") == target_id:
            return task
    return None


def update_task_data(task_id, new_data):
    target_id = str(task_id)
    tasks = read_csv(TASKS)
    updated = []

    for task in tasks:
        if task.get("task_id") == target_id:
            task.update(new_data)
        updated.append(task)

    overwrite_csv(TASKS, TASKS_FIELDNAMES, updated)


def delete_task_data(task_id):
    target_task_id = str(task_id)
    all_comments = read_csv(COMMENTS)
    
    comments_to_remove = [c for c in all_comments if str(c.get('task_id')) == target_task_id]
    
    for comment in comments_to_remove:
        delete_comment_data(comment['comment_id'])

    all_tasks = read_csv(TASKS)
    remaining_tasks = [t for t in all_tasks if str(t.get("task_id")) != target_task_id]
    overwrite_csv(TASKS, TASKS_FIELDNAMES, remaining_tasks)


# comentarios

def find_comments_by_task_id(task_id):
    comments = read_csv(COMMENTS)
    return [c for c in comments if str(c["task_id"]) == str(task_id)]

def find_comment_by_id(comment_id):
    comments = read_csv(COMMENTS)
    for c in comments:
        if str(c["comment_id"]) == str(comment_id):
            return c
    return None

def get_next_comment_id():
    comments = read_csv(COMMENTS)
    if not comments:
        return '1'
    max_id = max(int(c.get("comment_id", 0)) for c in comments)
    return str(max_id + 1)


def save_comment(comment):
    save_csv(COMMENTS, COMMENTS_FIELDNAMES, comment)


def update_comment_data(comment_id, new_content):
    comments = read_csv(COMMENTS)
    updated = False

    for c in comments:
        if str(c["comment_id"]) == str(comment_id):
            c["content"] = new_content
            updated = True
            break

    if updated:
        overwrite_csv(COMMENTS, COMMENTS_FIELDNAMES, comments)

    return updated


def delete_comment_data(comment_id):
    comments = read_csv(COMMENTS)
    new_comments = [c for c in comments if str(c["comment_id"]) != str(comment_id)]
    overwrite_csv(COMMENTS, COMMENTS_FIELDNAMES, new_comments)

