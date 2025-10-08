from decouple import config, UndefinedValueError

def get_db_config():
    try:
        return {
        'host': config('DB_HOST'),
        'user': config('DB_USER'),
        'password': config('DB_PASSWORD'),
        'database': config('DB_NAME'),
    }

    except UndefinedValueError as e:
        raise RuntimeError(f"Missing required database config: {e}")


