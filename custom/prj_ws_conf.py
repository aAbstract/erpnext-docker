import sys
import json
import mariadb


def database_connect() -> mariadb.Connection:
    DB_HOST = '127.0.0.1'
    DB_PORT = 3306
    DB_USER = 'root'
    DB_PASS = 'admin'
    MAIN_DB = '_5e5899d8398b5f7b'
    db_conn = mariadb.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=MAIN_DB,
    )
    return db_conn


def assign_to_user_filter() -> dict:
    return {'_assign': ['like', "'%' + frappe.session.user + '%'"]}


def status_filter(status: str) -> dict:
    return {'status': status}


def priority_filter(priority: str) -> dict:
    return {'priority': priority}


def post_process_filters(in_filters: str) -> str:
    out_filters = in_filters.replace("\"'%' + frappe.session.user + '%'\"", "'%' + frappe.session.user + '%'")
    return out_filters


def uconf_total_tasks_shortcut(db_conn: mariadb.Connection):
    cursor = db_conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM `tabWorkspace Shortcut` WHERE parent = 'Projects' AND label = 'Total Tasks';")
    record = cursor.fetchone()
    if not record:
        print('Error Can not Find `Total Tasks` Shortcut')
        sys.exit(1)

    stats_filter = assign_to_user_filter() | status_filter('Open')
    stats_filter = json.dumps(stats_filter)
    stats_filter = post_process_filters(stats_filter)

    cursor.execute("UPDATE `tabWorkspace Shortcut` SET stats_filter = ? WHERE parent = 'Projects' AND label = 'Total Tasks';", (stats_filter,))
    db_conn.commit()
    print(f'UPDATE `tabWorkspace Shortcut` Rows Affected: {cursor.rowcount}')


def ufconf_urgent_tasks_quick_list(db_conn: mariadb.Connection):
    cursor = db_conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM `tabWorkspace Quick List` WHERE parent = 'Projects' AND label = 'Urgent Tasks';")
    record = cursor.fetchone()
    if not record:
        print('Error Can not Find `Urgent Tasks` Quick List')
        sys.exit(1)

    quick_list_filter = assign_to_user_filter() | status_filter('Open') | priority_filter('Urgent')
    quick_list_filter = json.dumps(quick_list_filter)
    quick_list_filter = post_process_filters(quick_list_filter)

    cursor.execute("UPDATE `tabWorkspace Quick List` SET quick_list_filter = ? WHERE parent = 'Projects' AND label = 'Urgent Tasks';", (quick_list_filter,))
    db_conn.commit()
    print(f'UPDATE `tabWorkspace Quick List` Rows Affected: {cursor.rowcount}')


def main():
    db_conn = database_connect()

    uconf_total_tasks_shortcut(db_conn)
    ufconf_urgent_tasks_quick_list(db_conn)


if __name__ == '__main__':
    main()
