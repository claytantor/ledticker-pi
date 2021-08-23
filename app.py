from flask import Flask, jsonify, request
import utils

app = Flask(__name__)

@app.route('/message', methods=['POST'])
def save_message():

        # get the message
        request_data = request.get_json()

        # insert a record
        conn = utils.create_connection('db/led_messages.db')  
        m_id = utils.create_message(conn, request_data)  

        # return a value
        return jsonify(
            message_id=m_id,
            message="message created"
        )

if __name__ == "__main__":
    app.run(host='0.0.0.0')