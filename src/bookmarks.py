from crypt import methods
import validators, json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import Bookmark, db
from src.constants.http_status_code import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK
from flasgger import swag_from

bookmark = Blueprint("bookmark", __name__, url_prefix="/api/v1/bookmarks")

@bookmark.route('/', methods=['POST', 'GET'])
@jwt_required()
def handle_bookmark():
    current_user = get_jwt_identity() # get current user that already login

    if request.method == 'POST':

        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({
                'error': 'Enter a valid url'
            }), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error': 'URL already exists'
            }), HTTP_409_CONFLICT

        bookmark = Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visit,
            'body': bookmark.body,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at,
        }), HTTP_201_CREATED

    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        bookmarks = Bookmark.query.filter_by(
            user_id=current_user).paginate(page=page, per_page=per_page)

        data = []

        for bookmark in bookmarks.items:
            data.append({
                'id': bookmark.id,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visit': bookmark.visit,
                'body': bookmark.body,
                'created_at': bookmark.created_at,
                'updated_at': bookmark.updated_at,
            })

        meta = {
            "page": bookmarks.page,
            'pages': bookmarks.pages,
            'total_count': bookmarks.total,
            'prev_page': bookmarks.prev_num,
            'next_page': bookmarks.next_num,
            'has_next': bookmarks.has_next,
            'has_prev': bookmarks.has_prev,
        }

        return jsonify({'data': data, "meta": meta}), HTTP_200_OK

@bookmark.get('/<int:id>')
@jwt_required()
def getBookmark(id):
    current_user = get_jwt_identity() # get current user that just login

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()
    
    if not bookmark:
        return jsonify({"msg": "error user not found"}), HTTP_404_NOT_FOUND

    return jsonify({
        "id": bookmark.id,
        "user_id": bookmark.user_id,
        "body": bookmark.body,
        "short_url": bookmark.short_url,
        "url": bookmark.url,
        "visit": bookmark.visit,
        "created_at": bookmark.created_at,
        "updated_at": bookmark.updated_at
    }), HTTP_200_OK

# edit bookmark
@bookmark.route('/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def editBookmark(id):

    current_user = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    # if this bookmark not found
    if not bookmark:
        return jsonify({"msg": "error not found bookmark"}), HTTP_404_NOT_FOUND

    body = request.get_json().get('body', '')
    url  = request.get_json().get('url', '')

    # validate url
    if not validators.url(url):
        return jsonify({"msg": "invalid url"}), HTTP_400_BAD_REQUEST

    bookmark.body = body
    bookmark.url  = url

    db.session.commit()

    return jsonify({
        "id": bookmark.id,
        "user_id": bookmark.user_id,
        "body": bookmark.body,
        "short_url": bookmark.short_url,
        "url": bookmark.url,
        "visit": bookmark.visit,
        "created_at": bookmark.created_at,
        "updated_at": bookmark.updated_at
    }), HTTP_200_OK

# delete bookmark
@bookmark.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete(id):
    current_user = get_jwt_identity() # get current user who already login

    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first()

    # if this bookmark not found
    if not bookmark:
        return jsonify({"msg":"error not found bookmark"}), HTTP_404_NOT_FOUND
    
    # delete bookmark from database and commit to database
    db.session.delete(bookmark)
    db.session.commit()

    return jsonify(), HTTP_204_NO_CONTENT

# check link statistics. To see how many visits each link
@bookmark.get('/stat')
@jwt_required()
@swag_from('./docs/bookmarks/checkVisit.yml')
def checkVisit():
    # check current user
    current_user = get_jwt_identity()

    data = []

    bookmarks = Bookmark.query.filter_by(user_id=current_user).all()

    for bookmark in bookmarks:
        item = {
            "id": bookmark.id,
            "url": bookmark.url,
            "short_url": bookmark.short_url,
            "visit": bookmark.visit
        }
        data.append(item)

    return jsonify({"data": data}), HTTP_200_OK

# increase number of visit when go short url and redirect to url
@bookmark.get('/<short_url>')
@swag_from('./docs/short_url.yml')
def redirect_to_url(short_url):
    bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()

    # increase visit
    if bookmark:
        bookmark.visit = bookmark.visit+1
        db.session.commit()
        return jsonify({"short_url": short_url})
