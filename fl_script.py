from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import redis

app = Flask(__name__)
socketio = SocketIO(app)
r = redis.StrictRedis(host='localhost', port=6379, db=0)
setpoints_of_interest = ['desired_hdg', 'desired_alt', 'desired_speed']


# get initial setpoints from Redis, send to clients
@app.route('/')
def index():
    return render_template('index.html')


def update_setpoint(label, adjustment):
    # This function can be adapted to update setpoints and then emit updates via WebSocket
    current_value = float(r.get(label)) if r.exists(label) else 0.0
    if label == 'desired_hdg':
        new_value = (current_value + adjustment) % 360
    elif label == 'autopilot_enabled':
        new_value = adjustment
    else:
        new_value = current_value + adjustment
    r.set(label, new_value)
    # socketio.emit('update_setpoint', {label: new_value})  # Emit update to clients
    return new_value


@socketio.on('adjust_setpoint')
def handle_adjust_setpoint(json):
    label = json['label']
    adjustment = json['adjustment']
    # Your logic to adjust the setpoint in Redis and calculate new_value
    new_value = update_setpoint(label, adjustment)
    # Emit updated setpoint to all clients
    emit('update_setpoint', {label: new_value}, broadcast=True)


@socketio.on('connect')
def handle_connect(_):
    # Fetch initial setpoints from Redis
    initial_setpoints = {label: float(r.get(label)) if r.exists(label) else 0.0 for label in setpoints_of_interest}

    # Emit the initial setpoints to the connected client
    emit('update_setpoints', initial_setpoints)


if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True)