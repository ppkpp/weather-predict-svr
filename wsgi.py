from app import app, socketio

if __name__ == "__main__":
    # This will be used if you want to run the app directly for testing
    socketio.run(app, host='0.0.0.0', port=8889)
