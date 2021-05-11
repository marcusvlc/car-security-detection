import os.path
from flask import Blueprint, abort, Response, jsonify, request
from flask_cors import cross_origin
from app.__init__ import App
from app.ext import socketio
from app import models
import jwt
import datetime
from app.middlewares.autentication import jwt_required
from app.detection.stream import Detector
import numpy as np
import base64
import os
from app.serializable.model_serializable import streams_schema, plates_schema, stream_schema



blueprint = Blueprint('main', __name__, static_folder='static')
FILE_OUTPUT = 'output.avi'

@blueprint.route('/user/register', methods=['POST'])
@cross_origin()
def register_user():
    data = request.json
    name = data['name']
    email = data['email']
    password = data['password']
    try:
        user = models.User(name, email, password)
        models.db.session.add(user)
        models.db.session.commit()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': "Ocorreu um erro ao registrar"}), 500

@blueprint.route('/user/authenticated', methods=['GET'])
@jwt_required
def is_authenticated(current_user):
    return jsonify({"authenticated": True})


@blueprint.route('/user/login', methods=['POST'])
@cross_origin()
def login_user():
    try:
        data = request.json
        email = data['email']
        password = data['password']
        user = models.User.query.filter_by(email=email).first_or_404()

        if not user.verify_password(password):
            return jsonify({'error': "Credenciais incorretas"}), 403

        token_payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }

        token = jwt.encode(token_payload, App.get_app().config['SECRET_KEY'], algorithm="HS256")

        return jsonify({"token": token})
    except Exception as e:
        print(e)
        return jsonify({'error': "Ocorreu um erro ao autenticar"}), 500


@blueprint.route('/stream/register', methods=['POST'])
@cross_origin()
@jwt_required
def register_stream(current_user):
    data = request.form
    stream_type = data['stream_type']
    stream_name = data['stream_name']
    if(stream_type == "rtsp"):
        stream_url = data['stream_url']
        print(stream_url)
        stream = models.Stream(stream_name, stream_url, stream_type, None, current_user.id)
    else:
        stream_file = request.files['stream_file'].read()
        stream = models.Stream(stream_name, "", stream_type, stream_file, current_user.id)

    try:
        models.db.session.add(stream)
        models.db.session.commit()
        return jsonify({"success": True, "data": stream.to_json()})
    except Exception as e:
        print(e)
        return jsonify({'error': "Ocorreu um erro ao registrar a stream, tente novamente mais tarde"}), 500


@blueprint.route('/stream/all', methods=['GET'])
@cross_origin()
@jwt_required
def list_streams(current_user):
    page_number = int( request.args.get('page') or 1)
    all_streams = models.Stream.query.with_entities(models.Stream.id, models.Stream.name, models.Stream.stream_url, models.Stream.stream_type).filter_by(user_id=current_user.id)
    all_streams = all_streams.paginate(per_page=8, page=page_number, error_out=True)
    total_pages = all_streams.pages
    all_streams = streams_schema.dump(all_streams.items)
    return jsonify({'data': all_streams, 'total_pages': total_pages})


@blueprint.route('/detection/image', methods=['GET'])
@cross_origin()
@jwt_required
def detect_on_image(current_user):
    stream_id = request.args.get('stream_id')
    stream = models.Stream.query.get(stream_id)
    decoded = stream.get_decoded_file()
    detector = Detector(stream.stream_type, stream.id, None, stream.stream_type)
    values = detector.detect_on_image(decoded)
    image  = base64.b64encode(values["image"]).decode("ascii")
    return jsonify({"image": image, "plates": values["detected_plates"]})


@blueprint.route('/detection/video', methods=['GET'])
@cross_origin()
@jwt_required
def detect_on_video(current_user):
    stream_id = request.args.get('stream_id')
    stream = models.Stream.query.get(stream_id)


    detector = Detector(stream.stream_type, stream.id, stream.stream_file, stream.stream_url)
    return Response(detector.detect_on_video(),
                mimetype='multipart/x-mixed-replace; boundary=frame')

@blueprint.route('/plate/all', methods=['GET'])
@cross_origin()
@jwt_required
def get_all_user_plates(current_user):
    page_number = int( request.args.get('page') or 1)
    all_streams = models.Stream.query.with_entities(models.Stream.id).filter_by(user_id=current_user.id)
    all_plates = models.Plate.query.filter(models.Plate.stream_id.in_(all_streams))
    
    all_plates = all_plates.paginate(per_page=4, page=page_number, error_out=True)
    total_pages = all_plates.pages
    all_plates = plates_schema.dump(all_plates.items)

    return jsonify({"plates": all_plates, "total_pages": total_pages})


@blueprint.route('/stream', methods=['GET'])
@cross_origin()
@jwt_required
def get_stream_information(current_user):
    stream_id = request.args.get('stream_id')

    stream = models.Stream.query.with_entities(models.Stream.id, models.Stream.name, models.Stream.stream_url, models.Stream.stream_type).filter_by(user_id=current_user.id, id=stream_id).first_or_404()
    stream = stream_schema.dump(stream)

    return jsonify({"stream": stream})


@blueprint.route('/stream/delete', methods=['POST'])
@cross_origin()
@jwt_required
def delete_stream(current_user):
    data = request.json
    stream_id = data['stream_id']
    try:
        obj = models.Stream.query.filter_by(id=stream_id).one()
        models.db.session.delete(obj)
        models.db.session.commit()
        return jsonify({"deleted": True})
    except:
        return jsonify({"deleted": False})
    






