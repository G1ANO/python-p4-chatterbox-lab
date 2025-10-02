from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Extensions
CORS(app)
db.init_app(app)
migrate = Migrate(app, db)

# --------------------
# ROUTES
# --------------------

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.all()
        return jsonify([{
            "id": m.id,
            "body": m.body,
            "username": m.username,
            "created_at": m.created_at,
            "updated_at": m.updated_at
        } for m in messages]), 200

    elif request.method == 'POST':
        data = request.get_json()
        if not data or "body" not in data or "username" not in data:
            return make_response({"error": "Missing body or username"}, 400)

        new_message = Message(
            body=data["body"],
            username=data["username"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(new_message)
        db.session.commit()

        return jsonify({
            "id": new_message.id,
            "body": new_message.body,
            "username": new_message.username,
            "created_at": new_message.created_at,
            "updated_at": new_message.updated_at
        }), 201


@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get(id)
    if not message:
        return make_response({"error": "Message not found"}, 404)

    if request.method == 'GET':
        return jsonify({
            "id": message.id,
            "body": message.body,
            "username": message.username,
            "created_at": message.created_at,
            "updated_at": message.updated_at
        }), 200

    elif request.method == 'PATCH':
        data = request.get_json()
        if "body" in data:
            message.body = data["body"]
        if "username" in data:
            message.username = data["username"]
        message.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "id": message.id,
            "body": message.body,
            "username": message.username,
            "created_at": message.created_at,
            "updated_at": message.updated_at
        }), 200

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return make_response({"message": "Deleted successfully"}, 200)


# --------------------
# MAIN
# --------------------
if __name__ == '__main__':
    app.run(port=5555, debug=True)
