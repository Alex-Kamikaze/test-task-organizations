from sqlalchemy import Connection
from sqlalchemy.orm import object_session
from sqlalchemy.exc import IntegrityError
from ..models.activity_models import Activity


def check_activity_indentation_level(
    mapper: Activity, connection: Connection, target: Activity
):
    """
    Проверяет при каждом INSERT/UPDATE в таблицу Activity, что вложенность каталога видов деятельности не превышает трех уровней

    Args:
        mapper (Activity): Класс маппера
        connection (Connection): Соединение с базой
        target (Activity): Сущность, которая была вставлена/обновлена в базе

    Raises:
        IntegrityError: Если превышен уровень допустимой вложенности
    """

    if target.parent is None:
        return
    
    first_parent, second_parent, unallowed_parent = None, None, None
    
    session = object_session(target)
    if session is None:
        first_parent = connection.execute("SELECT parent FROM activities WHERE id = %s", (target.parent,)).fetchone()
        second_parent = connection.execute("SELECT parent FROM activities WHERE id = %s", (first_parent,)).fetchone()
        unallowed_parent = connection.execute("SELECT parent FROM activities WHERE id = %s", (second_parent, )).fetchone()
    else:
        first_parent = session.query(Activity).filter_by(id=target.parent).first()
        second_parent = session.query(Activity).filter_by(id=first_parent.parent).first()
        unallowed_parent = session.query(Activity).filter_by(id=second_parent.parent).first()

    if all((first_parent, second_parent, unallowed_parent)):
            raise IntegrityError("Нарушение уровней вложенности", None, None)