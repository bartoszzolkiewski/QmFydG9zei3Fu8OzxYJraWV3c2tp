from sanic.response import json
from sanic.exceptions import InvalidUsage, ServerError, NotFound
from sanic import Blueprint
from .classes import Url, History

api_bp = Blueprint('api', url_prefix='/api',)

@api_bp.route('/fetcher', methods=['POST'])
async def update(request):
    data = request.json

    url_id = data.get('id', None)
    url = data.get('url')
    interval = data.get('interval')

    if url_id:
        # nadpisujemy istniejacy url
        url_obj = Url.get_by_id(url_id)
        url_obj.update(url = url, interval = interval)

    else:
        # tworzymy nowy url
        url_obj = Url(url = url, interval = interval)

    if url_obj is None:
        # podano id url'a którego nie posiadamy w pamięci
        raise ServerError("Unknown obj id %s" % url_id, status_code = 400)

    return json(url_obj.as_dict(fields = ['id',]))

@api_bp.route('/fetcher/<url_id:int>', methods=['POST'])
async def retrieve(request, url_id):
    pass

@api_bp.route('/fetcher/<url_id:int>', methods=['DELETE'])
async def destroy(request, url_id):
    data = request.json

    url_obj = Url.get_by_id(url_id)

    if not url_obj:
        raise NotFound("Nie znaleziono obiektu")
        
    url_obj.remove()

    return json({})

@api_bp.route('/fetcher/', methods = ['GET'])
async def list_urls(request):
    return json([u.as_dict() for u in Url.get_all()])

@api_bp.route('/fetcher/<url_id>/history', methods = ['GET'])
async def list_history(request, url_id):

    try:
        url_id = int(url_id)
    except ValueError:
        raise InvalidUsage("Zły typ ID")
        
    url_obj = Url.get_by_id(url_id)

    if not url_obj:
        raise NotFound("Nie znaleziono obiektu")

    history_list = History.get_for_url(url_obj)

    return json(history_list)
