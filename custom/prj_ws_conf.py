import os
import sys
import json
import mariadb
from dotenv import load_dotenv


def database_connect() -> mariadb.Connection:

    db_conn = mariadb.connect(
        host=os.environ['DB_HOST'],
        port=int(os.environ['DB_PORT']),
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'],
        database=os.environ['MAIN_DB'],
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


def uconf_shortcuts(db_conn: mariadb.Connection, shortcut_label: str, status: str = 'Open', priority: str = None):
    cursor = db_conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM `tabWorkspace Shortcut` WHERE parent = 'Projects' AND label = ?;", (shortcut_label,))
    record = cursor.fetchone()
    if not record:
        print(f'Error Can not Find `{shortcut_label}` Shortcut')
        sys.exit(1)

    stats_filter = assign_to_user_filter() | status_filter(status)
    if priority:
        stats_filter |= priority_filter(priority)

    stats_filter = json.dumps(stats_filter)
    stats_filter = post_process_filters(stats_filter)

    cursor.execute("UPDATE `tabWorkspace Shortcut` SET stats_filter = ? WHERE parent = 'Projects' AND label = ?;", (stats_filter, shortcut_label))
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


def project_insert(db_conn: mariadb.Connection, project_name: str) -> str:
    sql = '''
        INSERT INTO tabProject
        (name, creation, modified, modified_by, owner, docstatus, idx, naming_series, project_name, status, project_type, is_active, percent_complete_method, percent_complete, project_template, expected_start_date, expected_end_date, priority, department, customer, sales_order, copied_from, notes, actual_start_date, actual_time, actual_end_date, estimated_costing, total_costing_amount, total_purchase_cost, company, total_sales_amount, total_billable_amount, total_billed_amount, total_consumed_material_cost, cost_center, gross_margin, per_gross_margin, collect_progress, holiday_list, frequency, from_time, to_time, first_email, second_email, daily_time_to_send, day_to_send, weekly_time_to_send, subject, message, _user_tags, _comments, _assign, _liked_by, _seen)
        VALUES(?, '2025-12-30 14:03:57.457', '2025-12-30 14:03:57.457', 'z.amin@lab-tronic.com', 'z.amin@lab-tronic.com', 0, 0, 'PROJ-.####', ?, 'Open', NULL, 'Yes', 'Task Completion', 0.000000000, NULL, NULL, NULL, 'Medium', NULL, NULL, NULL, NULL, NULL, NULL, 0.000000000, NULL, 0.000000000, 0.000000000, 0.000000000, 'LabTronic', 0.000000000, 0.000000000, 0.000000000, 0.000000000, NULL, 0.000000000, 0.000000000, 0, NULL, 'Hourly', NULL, NULL, NULL, NULL, NULL, 'Monday', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '["z.amin@lab-tronic.com"]');
    '''

    cursor = db_conn.cursor(dictionary=True)
    cursor.execute(sql, (project_name, project_name))
    db_conn.commit()
    print(f'Inserted Project `{project_name}`')


def main():
    load_dotenv('custom/.env')
    db_conn = database_connect()

    # uconf_shortcuts(db_conn=db_conn, shortcut_label='Total')
    # uconf_shortcuts(db_conn=db_conn, shortcut_label='Medium', priority='Medium')
    # uconf_shortcuts(db_conn=db_conn, shortcut_label='High', priority='High')
    # uconf_shortcuts(db_conn=db_conn, shortcut_label='Urgent', priority='Urgent')

    # uconf_shortcuts(db_conn=db_conn, shortcut_label='Working', status='Working')
    # uconf_shortcuts(db_conn=db_conn, shortcut_label='Pending', status='Pending Review')
    # uconf_shortcuts(db_conn=db_conn, shortcut_label='Overdue', status='Overdue')

    # ufconf_urgent_tasks_quick_list(db_conn)

    with open('custom/Old_Projects.txt', 'r') as f:
        lines = f.readlines()
        for project_name in lines:
            project_insert(db_conn=db_conn, project_name=project_name.strip())


if __name__ == '__main__':
    main()
