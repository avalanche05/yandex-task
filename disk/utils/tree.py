from sqlalchemy.orm import Session

from disk.db import db_session, models

db_sess = None
db_sess: Session


def recursion_tree(item_id: str) -> dict:
    children = []
    item = db_sess.query(models.items.Item).filter_by(id=item_id).first()
    item: models.items.Item
    for child in item.get_children_id():
        children.append(recursion_tree(child))

    result = {
        'id': item_id,
        'url': item.url,
        'type': item.type,
        'parentId': item.parent_id,
        'date': item.date,
        'size': item.size if item.type == 'FILE' else sum(
            list(map(lambda x: x['size'], children)) + [0]),
        'children': children if children else None

    }

    return result


def get_tree(item_id: str) -> dict:
    global db_sess
    db_sess = db_session.create_session()
    if db_sess.query(models.items.Item).filter_by(id=item_id).count() < 1:
        raise ValueError

    result = recursion_tree(item_id)

    db_sess.commit()
    db_sess.close()

    return result
