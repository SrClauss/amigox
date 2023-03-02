from datetime import datetime
from flask import jsonify, request
from models import User, Group, Friend, db, app
import random

SECRET_KEY = "CLAUSEMBERG"


def req_check(request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return False
    if auth_header != SECRET_KEY:
        return False
    return True


@app.route("/users", methods=["GET"])
def get_all_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users])


@app.route("/groups", methods=["GET"])
def get_all_groups():
    groups = Group.query.all()
    return jsonify([group.serialize() for group in groups])


@app.route("/friends", methods=["GET"])
def get_all_friends():
    friends = Friend.query.all()
    return jsonify([friend.serialize() for friend in friends])


@app.route("/user/<user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({"error": "User not found"}), 404


@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return jsonify({'name': user.name, 'email': user.email, 'phone': user.phone})
    return jsonify({'error': 'Invalid email or password'}), 401


@app.route("/group/<group_id>", methods=["GET"])
def get_group(group_id):
    group = Group.query.filter_by(id=group_id).first()
    if group:
        return jsonify(group.to_dict()), 200
    return jsonify({"error": "Group not found"}), 404


@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    password = data.get('password')

    user = User(name=name, phone=phone, email=email, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User added successfully'}), 201


@app.route('/groups', methods=['POST'])
def add_group():
    data = request.get_json()
    name = data.get('name')
    host = data.get('host')
    created_at = datetime.strptime(data.get('created_at'), "%Y-%m-%d %H:%M:%S")
    event_date = datetime.strptime(data.get('event_date'), "%Y-%m-%d %H:%M:%S")
    allow_break = data.get('allow_break')
    max_value = data.get('max_value')
    min_value = data.get('min_value')

    group = Group(name=name, host=host, created_at=created_at, event_date=event_date,
                  allow_break=allow_break, max_value=max_value, min_value=min_value)
    db.session.add(group)
    db.session.commit()

    return jsonify({'message': 'Group added successfully'}), 201


@app.route('/friends', methods=['POST'])
def add_friend():
    data = request.get_json()
    user_id = data.get('user_id')
    group_id = data.get('group_id')
    sorted_friend_id = data.get('sorted_friend_id')
    desired_gift = data.get('desired_gift')

    friend = Friend(user_id=user_id, group_id=group_id, sorted_friend_id=sorted_friend_id, desired_gift=desired_gift)
    db.session.add(friend)
    db.session.commit()

    return jsonify({'message': 'Friend added successfully'}), 201


@app.route('/sort_friends', methods=['POST'])
def sort_friends():
    data = request.get_json()
    # Recupera todos os objetos Friend que tem o group_id especificado
    friends = Friend.query.filter_by(group_id=data.get('group_id')).all()

    # Verifica se a quantidade de amigos é maior ou igual a 3
    if len(friends) < 3:
        return jsonify({"error": "Número de amigos insuficiente para realizar o sorteio."}), 400

    # Recupera o objeto Group que tem o group_id especificado
    group = Group.query.filter_by(id=data.get('group_id')).first()
    if group.sorted:
        return jsonify({"error": "Este Grupo já foi sorteado"}), 400
    # Faz uma cópia da lista de friends
    friends_copy = list(friends)

    # Verifica se allow_break é verdadeiro
    if group.allow_break:
        # Cria uma lista indexes com todos os índices dos friends
        indexes = list(range(len(friends_copy)))

        for i in range(len(friends_copy)):
            # Sorteia um elemento da lista indexes
            friend_index = random.choice(indexes)

            # Verifica se o índice sorteado é o índice do próprio friend
            while friend_index == i:
                # Faz um novo sorteio
                friend_index = random.choice(indexes)

            # Atribui o friend sorteado ao amigo
            friends_copy[i].sorted_friend_id = friends_copy[friend_index].user_id

            # Remove o índice sorteado da lista indexes
            indexes.remove(friend_index)

            # Verifica se o último sorteado é ele mesmo
            if i == len(friends_copy) - 1 and friends_copy[i].sorted_friend_id == friends_copy[i].user_id:
                # Faz uma nova atribuição da lista copia (zera ela) e reinicia o sorteio
                friends_copy = list(friends)
                indexes = list(range(len(friends_copy)))
                i = -1
    else:
        # Faz o embaralhamento da lista copia
        random.shuffle(friends_copy)

        # Faz o esquema que o primeiro tira o segundo, que tira o terceiro até o ultimo que tira o primeiro
        for i in range(len(friends_copy) - 1):
            friends_copy[i].sorted_friend_id = friends_copy[i + 1].user_id
        friends_copy[-1].sorted_friend = friends_copy[0]

    # Salva as informações no banco de dados
    try:
        # Salva as informações no banco de dados
        for friend in friends_copy:
            group.sorted = True
            db.session.add(group)
            db.session.add(friend)
            db.session.flush()
            db.session.commit()
    except Exception as e:
        # Retorna um erro para o usuário
        return jsonify({"error": str(e)}), 500

    # Retorna sucesso

    return jsonify({"message": "Sucess."}), 200


@app.route("/user/sorted", methods=["POST"])
def get_user_sort():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if email is None or password is None:
        return jsonify({"message": "Both email and password are required"}), 200

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"message": "User not found"}), 404
    if not user.check_password(password):
        return jsonify({"message": "Incorrect password"}), 401

    friends = Friend.query.filter_by(user_id=user.id).all()
    results = []
    for friend in friends:
        group = Group.query.filter_by(id=friend.group_id).first()
        sorted_friend = User.query.filter_by(id=friend.sorted_friend_id).first()
        result = {
            "group_id": group.id,
            "event_date": group.event_date.strftime("%Y-%m-%d %H:%M:%S"),
            "sorted_friend": sorted_friend.serialize()
        }
        results.append(result)
    return jsonify(results), 200


@app.route("/group/host", methods=["POST"])
def get_groups_as_host():
    email = request.json.get("email")
    password = request.json.get("password")

    user = User.query.filter_by(email=email).first()

    if user is None or not user.check_password(password):
        return jsonify({"message": "Unauthorized"}), 401

    groups = Group.query.filter_by(host=user.id).all()

    return jsonify([group.serialize() for group in groups]), 200


@app.route("/group/god", methods=["POST"])
def get_all_group_info():
    data = request.get_json()
    friends = db.session.query(Friend).filter_by(group_id=data['group_id']).all()

    if len(data['logins']) > len(friends) / 3:
        for log in data['logins']:
            user = db.session.query(User).filter_by(email=log['email']).first()
            if user.check_password(log['password']):
                continue
            else:
                return jsonify({'status': "O participante {0} inseriu o login errado,"
                                          "o processo foi interrompido".format(user.name)}), 412
        return jsonify([x.serialize() for x in friends])

    else:
        return jsonify({"status": "A quantidade de logins de participantes que autorizam ver as informações é "
                                  "insuficiente"}), 401


if __name__ == '__main__':
    app.run(debug=True)
