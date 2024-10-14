import json
import time
from flask import Flask, make_response, send_file, request, redirect, abort, Response
import os
import mimetypes

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/javascript', '.mjs')
mimetypes.add_type('text/css', '.css')

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
banned_paths = [".py"]

client_id_count = 0
client_timeout = 5
clients = {}
messages = []


@app.errorhandler(404)
def page_not_found(e):
    return {"error": "Not found"}, 404


@app.route('/')
def home_page():
    resp = make_response(send_file("index.html"))
    return resp


@app.route('/<path:filename>')
def getfile(filename):

    for x in range(len(banned_paths)):
        if banned_paths[x] in filename:
            return abort(404), 404

    if filename[-1] == "/":

        if os.path.isfile("index.html"):

            return send_file("index.html")

        else:

            return abort(404), 404

    elif "." not in filename:

        if os.path.isfile("index.html"):

            return send_file("index.html")

        else:

            return abort(404), 404

    elif filename[-3:] == ".js":
        print("js")
        if os.path.isfile(filename):

            return send_file(filename, "application/javascript")

        else:

            return abort(404), 404

    else:

        if os.path.isfile(filename):

            return send_file(filename)

        else:

            return abort(404), 404


def clear_expired_clients():
    current_time = time.time()
    expired_clients = [client_id for client_id, client in clients.items() if client['expires'] < current_time]
    for client_id in expired_clients:
        del clients[client_id]


@app.route('/api/chat/get_messages')
def get_messages():

    global client_id_count

    client_id = client_id_count
    client_id_count += 1

    clients[client_id] = {"id": client_id, "messages": [], "expires": time.time() + client_timeout}

    return {"messages": messages, "client_id": client_id}, 200


@app.route('/api/chat/events')
def chat_events():

    client_id = int(request.args.get("client_id"))

    clients[client_id]["expires"] = time.time() + client_timeout

    clear_expired_clients()

    print(json.dumps(clients, indent=4))

    def execute_events():
        for i in range(len(clients[client_id]["messages"])):
            yield f'id:1\ndata: {json.dumps(clients[client_id]["messages"][0])}\nevent: message\n\n'
            clients[client_id]["messages"].pop(0)
    
    return Response(execute_events(), mimetype='text/event-stream')


@app.route('/api/chat/send_message', methods=['POST'])
def send_message():
    for client in clients:
        
        if client == int(request.args.get("client_id")):
            continue

        clear_expired_clients()

        if client in clients:
            clients[client]['messages'].append(request.json['message'])


    messages.append(request.json['message'])
    if len(messages) > 100:
        messages.pop(0)
    return {"status": "ok"}, 200
    

app.run(host='0.0.0.0', port=12000, use_reloader=True)
