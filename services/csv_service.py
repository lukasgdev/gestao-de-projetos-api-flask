# services/csv_service.py
# Funções para ler, escrever, gerar ID e manipular CSVs de users, projects e tasks.
import os
import csv
from typing import List, Dict, Any

# paths
current_path = os.path.dirname(os.path.abspath(__file__))
main_path = os.path.dirname(current_path)
db_path = os.path.join(main_path, "db")

USERS = os.path.join(db_path, "users.csv")
PROJECTS = os.path.join(db_path, "projects.csv")
TASKS = os.path.join(db_path, "tasks.csv")

# fieldnames (ATENÇÃO: TASKS agora inclui user_id)
USER_FIELDNAMES = ["user_id", "name", "email", "password_hash", "created_on"]
PROJECT_FIELDNAMES = ["project_id", "user_id", "project_title", "project_description", "created_on"]
TASK_FIELDNAMES = ["task_id", "title", "description", "status", "project_id", "user_id"]


# -------------------------
# Helpers genéricos de CSV
# -------------------------
def _ensure_db_folder():
    if not os.path.exists(db_path):
        os.makedirs(db_path, exist_ok=True)


def save_csv(arq: str, fieldnames: List[str], data: Dict[str, Any]) -> None:
    """Anexa uma linha ao CSV; cria header se arquivo não existir ou estiver vazio."""
    _ensure_db_folder()
    mode = "a"
    write_header = not os.path.exists(arq) or os.path.getsize(arq) == 0
    with open(arq, mode, encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        # Garantir que o dicionário contenha todas as chaves (preencher com '')
        row = {k: ("" if data.get(k) is None else str(data.get(k))) for k in fieldnames}
        writer.writerow(row)


def overwrite_csv(arq: str, fieldnames: List[str], data_list: List[Dict[str, Any]]) -> None:
    """Sobrescreve o CSV por completo com data_list (lista de dicionários)."""
    _ensure_db_folder()
    with open(arq, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        rows = []
        for d in data_list:
            row = {k: ("" if d.get(k) is None else str(d.get(k))) for k in fieldnames}
            rows.append(row)
        writer.writerows(rows)


def read_csv(arq: str) -> List[Dict[str, str]]:
    """Retorna lista de dicionários lidos do CSV. Nunca modifica os dicionários lidos."""
    try:
        if not os.path.exists(arq):
            return []
        with open(arq, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [dict(row) for row in reader]
    except Exception as e:
        print(f"Erro ao ler o CSV {arq}: {e}")
        return []


# -------------------------
# IDs auto-incrementais
# -------------------------
def _get_next_id_for(arq: str, id_field: str) -> int:
    rows = read_csv(arq)
    if not rows:
        return 1
    max_id = 0
    for r in rows:
        try:
            v = int(r.get(id_field, 0))
        except Exception:
            v = 0
        if v > max_id:
            max_id = v
    return max_id + 1


def get_next_user_id() -> int:
    return _get_next_id_for(USERS, "user_id")


def get_next_project_id() -> int:
    return _get_next_id_for(PROJECTS, "project_id")


def get_next_task_id() -> int:
    return _get_next_id_for(TASKS, "task_id")


# -------------------------
# Users
# -------------------------
def save_user(user: Dict[str, Any]) -> None:
    save_csv(USERS, USER_FIELDNAMES, user)


def find_user_by_email(email: str) -> Dict[str, str] | None:
    users = read_csv(USERS)
    for u in users:
        if u.get("email") == email:
            return u
    return None


def find_user_by_id(user_id: Any) -> Dict[str, str] | None:
    target = str(user_id)
    users = read_csv(USERS)
    for u in users:
        if u.get("user_id") == target:
            return u
    return None


def update_user_data(user_id: Any, new_data: Dict[str, Any]) -> None:
    users = read_csv(USERS)
    target = str(user_id)
    updated = []
    for u in users:
        if u.get("user_id") == target:
            u = {**u, **{k: str(v) for k, v in new_data.items()}}
        updated.append(u)
    overwrite_csv(USERS, USER_FIELDNAMES, updated)


def delete_user_data(user_id: Any) -> None:
    users = read_csv(USERS)
    target = str(user_id)
    remaining = [u for u in users if u.get("user_id") != target]
    overwrite_csv(USERS, USER_FIELDNAMES, remaining)


# -------------------------
# Projects
# -------------------------
def save_project(project: Dict[str, Any]) -> None:
    save_csv(PROJECTS, PROJECT_FIELDNAMES, project)


def find_project_by_id(project_id: Any) -> Dict[str, str] | None:
    target = str(project_id)
    projects = read_csv(PROJECTS)
    for p in projects:
        if p.get("project_id") == target:
            return p
    return None


def find_projects_by_user_id(user_id: Any) -> List[Dict[str, str]]:
    """Retorna lista de projetos do usuário. NÃO muta os dicionários originais."""
    projects = read_csv(PROJECTS)
    target = str(user_id)
    result = []
    for p in projects:
        if p.get("user_id") == target:
            # criar cópia para evitar mutações
            result.append(dict(p))
    return result


def update_project_data(project_id: Any, new_data: Dict[str, Any]) -> None:
    projects = read_csv(PROJECTS)
    target = str(project_id)
    updated = []
    for p in projects:
        if p.get("project_id") == target:
            p = {**p, **{k: str(v) for k, v in new_data.items()}}
        updated.append(p)
    overwrite_csv(PROJECTS, PROJECT_FIELDNAMES, updated)


def delete_project_data(project_id: Any) -> None:
    projects = read_csv(PROJECTS)
    target = str(project_id)
    remaining = [p for p in projects if p.get("project_id") != target]
    overwrite_csv(PROJECTS, PROJECT_FIELDNAMES, remaining)


# -------------------------
# Tasks
# -------------------------
def save_task(task: Dict[str, Any]) -> None:
    # Garantir que as chaves existam e sejam string
    row = {k: ("" if task.get(k) is None else str(task.get(k))) for k in TASK_FIELDNAMES}
    save_csv(TASKS, TASK_FIELDNAMES, row)


def find_task_by_id(task_id: Any) -> Dict[str, str] | None:
    target = str(task_id)
    tasks = read_csv(TASKS)
    for t in tasks:
        if t.get("task_id") == target:
            return t
    return None


def find_tasks_by_project(project_id: Any) -> List[Dict[str, str]]:
    target = str(project_id).strip()
    tasks = read_csv(TASKS)
    result = []
    for t in tasks:
        if t.get("project_id", "").strip() == target:
            result.append(dict(t))  # devolve cópia
    return result


def update_task_data(task_id: Any, new_data: Dict[str, Any]) -> None:
    tasks = read_csv(TASKS)
    target = str(task_id)
    updated = []
    for t in tasks:
        if t.get("task_id") == target:
            t = {**t, **{k: str(v) for k, v in new_data.items()}}
        updated.append(t)
    overwrite_csv(TASKS, TASK_FIELDNAMES, updated)


def delete_task_data(task_id: Any) -> None:
    tasks = read_csv(TASKS)
    target = str(task_id)
    remaining = [t for t in tasks if t.get("task_id") != target]
    overwrite_csv(TASKS, TASK_FIELDNAMES, remaining)


# -------------------------
# FIM
# -------------------------
