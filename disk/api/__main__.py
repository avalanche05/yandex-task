import logging

import aiohttp.web_request
from aiohttp import web
from aiomisc import bind_socket

from disk.db import db_session
from disk.db import models
from disk.utils.erase import erase
from disk.utils.tree import get_tree
from disk.utils.validation import datetime_valid

routes = web.RouteTableDef()


@routes.post('/imports')
async def imports(request: aiohttp.web_request.Request):
    items = []
    try:
        json_data = await request.json()
        update_date = json_data['updateDate']
        for item in json_data['items']:
            item: dict
            db_item = models.items.Item()
            item_id = item['id']
            parent_id = item.get('parentId', None)

            db_item.id = item_id
            db_item.parent_id = parent_id
            if not datetime_valid(update_date):
                raise KeyError
            db_item.date = update_date

            if 'FILE' == item['type']:
                size = int(item['size'])
                url = item.get('url', None)

                db_item.size = size
                db_item.url = url
            elif 'FOLDER' == item['type']:
                pass
            else:
                raise KeyError
            db_item.type = item['type']
            items.append(db_item)
    except KeyError:
        result = {
            "code": 400,
            "message": "Validation Failed"
        }
        return web.json_response(result, status=400)

    db_sess = db_session.create_session()

    for item in items:
        item: models.items.Item
        if db_sess.query(models.items.Item).filter_by(id=item.id).count() < 1:
            db_sess.add(item)
        else:
            old_item = db_sess.query(models.items.Item).filter_by(id=item.id).first()
            old_item: models.items.Item
            old_item.copy(item)

        if not item.parent_id is None and item.parent_id:
            try:
                parent = db_sess.query(models.items.Item).filter_by(id=item.parent_id).first()
                parent: models.items.Item
                parent.add_child(item.id)
            except Exception as e:
                print(e)
                db_sess.close()
                result = {
                    "code": 400,
                    "message": "Validation Failed"
                }
                return web.json_response(result, status=400)
    db_sess.commit()
    db_sess.close()
    return web.Response(status=200)


@routes.delete('/delete/{id}')
def delete(request: aiohttp.web_request.Request):
    item_id = request.match_info.get('id', None)
    try:
        date = request.rel_url.query['date']
        if not datetime_valid(date):
            result = {
                "code": 400,
                "message": "Validation Failed"
            }
            return web.json_response(result, status=400)
    except Exception:
        result = {
            "code": 400,
            "message": "Validation Failed"
        }
        return web.json_response(result, status=400)
    if item_id is None:
        result = {
            "code": 400,
            "message": "Validation Failed"
        }
        return web.json_response(result, status=400)
    try:
        erase(item_id)
    except ValueError:
        result = {
            "code": 404,
            "message": "Item not found"
        }
        return web.json_response(result, status=404)
    return web.Response(status=200)


@routes.get('/nodes/{id}')
def nodes(request: aiohttp.web_request.Request):
    item_id = request.match_info.get('id', None)
    if item_id is None:
        result = {
            "code": 400,
            "message": "Validation Failed"
        }
        return web.json_response(result, status=400)

    try:
        result = get_tree(item_id)
        return web.json_response(result, status=200)
    except ValueError:
        result = {
            "code": 404,
            "message": "Item not found"
        }


def main():
    logging.basicConfig(level=logging.DEBUG)

    db_session.global_init("../db/data.db")

    sock = bind_socket(address='0.0.0.0', port=8080, proto_name='http')

    app = web.Application()
    app.router.add_routes(routes)
    web.run_app(app, sock=sock)


if __name__ == '__main__':
    main()
