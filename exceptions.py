import traceback


def exception_message(e_name: str, e: Exception):
    print(f"\n{e_name.upper()}:\n {e}")
    print(traceback.format_exc())


def db_changing_exception(e: Exception):
    exception_message("Ошибка обновления данных в бд", e)


def web_exception(e: Exception):
    exception_message("Ошибка при работе с сайтом", e)
