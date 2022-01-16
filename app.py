from flask import Flask, jsonify, request
import utils

app = Flask(__name__)
# conn = utils.create_connection('/home/pi/projects/ledticker-pi/db/led_messages.db') 

def get_db_connection():
    conn = sqlite3.connect('/home/pi/projects/ledticker-pi/db/led_messages.db')
    conn.row_factory = sqlite3.Row
    return conn



@app.route('/message', methods=['POST'])
def save_message():

        # get the message
        request_data = request.get_json()

        # insert a record
        conn = utils.create_connection('/home/pi/projects/ledticker-pi/db/led_messages.db')  
        m_id = utils.create_message(conn, request_data)  

        # return a value
        return jsonify(
            message_id=m_id,
            message="message created"
        )



@app.route('/message', methods=['GET'])
def get_messages():
   conn = utils.create_connection('/home/pi/projects/ledticker-pi/db/led_messages.db') 
   l_m = utils.select_all_messages(conn)
   utils.delete_all_messages(conn)
   return jsonify(l_m), 200




if __name__ == "__main__":
    app.run(host='0.0.0.0')
