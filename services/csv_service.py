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
USERS = os.path.join(db_path, "usuarios.csv")

def save_csv (arq, fieldnames, data):
    with open(arq, 'a', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if os.path.getsize(arq) == 0:
            writer.writeheader()

        writer.writerow(data)

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
    
    max_id = 0
    for user in users:
        user_id = int(user.get('user_id', 0))
        if user_id > max_id:
            max_id = user_id
    
    return max_id + 1

def save_user(user):
    USER_FIELDNAMES = ['user_id', 'name', 'email', 'password_hash']
    save_csv(USERS, USER_FIELDNAMES, user)