import sqlalchemy

from ..db_session import SqlAlchemyBase


class Item(SqlAlchemyBase):
    __tablename__ = 'items'

    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    type = sqlalchemy.Column(sqlalchemy.String)
    parent_id = sqlalchemy.Column(sqlalchemy.String)
    children_id = sqlalchemy.Column(sqlalchemy.String)
    url = sqlalchemy.Column(sqlalchemy.String)
    size = sqlalchemy.Column(sqlalchemy.Integer)
    date = sqlalchemy.Column(sqlalchemy.String)

    def add_child(self, child_id: str) -> None:
        if self.children_id is None or not self.children_id:
            self.children_id = child_id
        else:
            self.children_id += '~' + child_id

    def get_children_id(self) -> list:
        if self.children_id is None:
            return []
        return self.children_id.split('~')

    def delete_children_id(self, child_id: str) -> None:
        children = self.get_children_id()
        children.remove(child_id)
        self.children_id = '~'.join(children)

    def copy(self, item):
        self.type = item.type
        self.parent_id = item.parent_id
        self.children_id = item.children_id
        self.url = item.url
        self.size = item.size
        self.date = item.date
