# funções para ler, escrever, gerar ID e etc para os arquivos CSV
import os
import csv

# caminho da pasta atual
current_path = os.path.dirname(os.path.abspath(__file__))

# caminho da pasta raiz do projeto
main_path = os.path.dirname(current_path)

# caminho para a pasta 'db' com os arquivos csv
db_path = os.path.join(main_path, 'db')

# caminho especifico dos arquivos
USERS = os.path.join(db_path, "users.csv")
PROJECTS = os.path.join(db_path, "projects.csv")
LISTS = os.path.join(db_path, "lists.csv")
TASKS = os.path.join(db_path, "tasks.csv")

USER_FIELDNAMES = ['user_id', 'name', 'email', 'password_hash', 'created_on']
PROJECT_FIELDNAMES = ['project_id', 'user_id', 'project_title', 'project_description','created_on']
LIST_FIELDNAMES = ['list_id', 'project_id', 'list_name', 'created_on']
TASKS_FIELDNAMES = ['task_id','title','description','status','created_on','list_id']

def save_csv (arq, fieldnames, data):
    with open(arq, 'a', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if os.path.getsize(arq) == 0:
            writer.writeheader()

        writer.writerow(data)

def overwrite_csv(arq, fieldnames, data_list):
    with open(arq, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
    
        writer.writerows(data_list)

def read_csv (arq):
    try:
        with open(arq, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except Exception as e:
        print(f'Erro ao ler o CSV {arq}: {e}')
        return []
    
def find_user_by_email(email):
    users = read_csv(USERS)
    for user in users:
        if user.get('email') == email:
            return user
    return None

def find_user_by_id(user_id):
    users = read_csv(USERS)
    target_id = str(user_id) 
    for user in users:
        if user.get('user_id') == target_id:
            return user
    return None

def get_next_user_id():
    users = read_csv(USERS)

    if not users:
        return 1
    
    max_id = 0
    for user in users:
        user_id = int(user.get('user_id', 0))
        if user_id > max_id:
            max_id = user_id
    
    return max_id + 1

def get_next_project_id():
    projects = read_csv(PROJECTS)

    if not projects:
        return 1
    
    max_id = 0
    for project in projects:
        project_id = int(project.get('project_id', 0))
        if project_id > max_id:
            max_id = project_id
    
    return max_id + 1

def update_user_data(user_id, new_data):
    users = read_csv(USERS)
    updated_users_list = []
    target_id = str(user_id) 
    for user in users:
        if user["user_id"] == target_id:
            user.update(new_data)
        updated_users_list.append(user)
    
    overwrite_csv(USERS, USER_FIELDNAMES, updated_users_list)

def update_project_data(project_id, new_data):
    projects = read_csv(PROJECTS)
    updated_projects_list = []
    target_id = str(project_id)
 
    for project in projects:
        if project.get('project_id') == target_id:
            project.update(new_data)  # Atualiza o dicionário
        updated_projects_list.append(project)
     
    overwrite_csv(PROJECTS, PROJECT_FIELDNAMES, updated_projects_list)

def delete_project_data(project_id):
    projects = read_csv(PROJECTS)
    target_id = str(project_id) 
     
    remaining_projects = [
        project for project in projects 
        if project.get('project_id') != target_id
    ]
    
    overwrite_csv(PROJECTS, PROJECT_FIELDNAMES, remaining_projects)

def find_project_by_id(project_id):
    projects = read_csv(PROJECTS)
    target_id = str(project_id) 
    for project in projects:
        if project.get('project_id') == target_id:
            return project
    return None

def find_projects_by_user_id(user_id):
    all_projects = read_csv(PROJECTS)

    user = find_user_by_id(user_id)
    
    my_projects = []
    target_user_id = str(user_id) 
 
    for project in all_projects:
        project_user_id = project.get('user_id')
        if project_user_id == target_user_id:
            project.pop('user_id')
            project['owner_user'] = user['name']
            my_projects.append(project)
             
    return my_projects

def delete_user_data(user_id):
    users = read_csv(USERS)
    target_id = str(user_id) 
    users = [user for user in users if user['user_id'] != target_id]

    overwrite_csv(USERS,USER_FIELDNAMES,users)

def save_user(user):
    save_csv(USERS, USER_FIELDNAMES, user)

def save_project(project):
    save_csv(PROJECTS, PROJECT_FIELDNAMES, project)

def get_next_list_id():
    lists = read_csv(LISTS)
    if not lists:
        return 1
    max_id = 0
    for list in lists:
        lists_id = int(list.get('list_id', 0))
        if lists_id > max_id:
            max_id = lists_id
    return max_id + 1

def save_list(lista_data):
    save_csv(LISTS, LIST_FIELDNAMES, lista_data)

def find_lists_by_project_id(project_id):
    all_lists = read_csv(LISTS)
    project_lists = []
    target_id = str(project_id)
    
    for list in all_lists:
        if list.get('project_id') == target_id:
            project_lists.append(list)
            
    return project_lists

def find_list_by_id(list_id):
    lists = read_csv(LISTS)
    target_id = str(list_id)
    for list in lists:
        if list.get('list_id') == target_id:
            return list
    return None

def delete_list_data(list_id):
    lists = read_csv(LISTS)
    target_id = str(list_id)
    
    # Filtra a lista mantendo apenas as que NÃO são o alvo
    remaining_lists = [l for l in lists if l.get('list_id') != target_id]
    
    overwrite_csv(LISTS, LIST_FIELDNAMES, remaining_lists)

def update_list_data(list_id, new_data):
    lists = read_csv(LISTS)
    target_id = str(list_id)
    updated_lists = []

    for list in lists:
        if list.get('list_id') == target_id:
            list.update(new_data) # Atualiza os campos
        updated_lists.append(list)
    
    overwrite_csv(LISTS, LIST_FIELDNAMES, updated_lists)