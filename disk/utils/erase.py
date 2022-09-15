from sqlalchemy.orm import Session

from disk.db import db_session, models

db_sess = None
db_sess: Session


def recursion_erase(item_id: str) -> None:
    item = db_sess.query(models.items.Item).filter_by(id=item_id).first()
    item: models.items.Item
    for child_id in item.get_children_id():
        recursion_erase(child_id)
    db_sess.query(models.items.Item).filter_by(id=item_id).delete()


def erase(item_id: str) -> None:
    global db_sess
    db_sess = db_session.create_session()
    if db_sess.query(models.items.Item).filter_by(id=item_id).count() < 1:
        raise ValueError
    item = db_sess.query(models.items.Item).filter_by(id=item_id).first()
    item: models.items.Item
    if not item.parent_id is None and item.parent_id:
        parent = db_sess.query(models.items.Item).filter_by(id=item.parent_id).first()
        parent: models.items.Item
        parent.delete_children_id(item.id)

    recursion_erase(item_id)

    db_sess.commit()
    db_sess.close()
