import os,sys
import utils


db_file = '/home/pi/projects/ledticker-pi/db/led_messages.db'



def get_messages(conn):
   l_m = utils.select_all_messages(conn)
   utils.delete_all_messages(conn)
   return l_m

def main(argv):
    print("starting db init")
    conn = utils.create_connection(db_file)
    get_messages(conn) 


if __name__ == "__main__":
    main(sys.argv[1:])
