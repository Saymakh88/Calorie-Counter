from django.db import connection

def run_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        result = cursor.fetchall()
    return result
