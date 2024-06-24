import cmd
import ipaddress
import socket

def login(socket:socket.socket, login:str, password:str):

    msg = int(0).to_bytes() + len(login.encode()).to_bytes() + login.encode("utf-8") + len(password.encode()).to_bytes() + password.encode("utf-8")
    socket.send(len(msg).to_bytes(3)+msg)

    r = socket.recv(4)
    if r == bytes([255,255,255,255]):
        return 0
    return 1

def get_messages(socket:socket.socket, count: int, offset: int, rcontacts: dict):
    msg = int(2).to_bytes() + count.to_bytes(2) + offset.to_bytes(4)
    socket.send(len(msg).to_bytes(3)+msg)

    ok = socket.recv(4)
    if ok == bytes([255,255,255,255]):
        
        n = int.from_bytes(socket.recv(2))
        for i in range(n):
            msg_len = int.from_bytes(socket.recv(3),byteorder='little')
            text_len = int.from_bytes(socket.recv(2), byteorder='little')
            text = socket.recv(text_len)
            sender_addr = ipaddress.IPv6Address(socket.recv(16))
            time = int.from_bytes(socket.recv(8), byteorder='little')
            msgid = socket.recv(4)
            msgid = int.from_bytes(msgid, byteorder='little')
            if sender_addr not in rcontacts.keys():
                print(f"{sender_addr} {time} |{msgid}| {text}")
            else:
                print(f"{rcontacts[sender_addr]} {time} |{msgid}| {text}")
        return n
    else:

        print("err get messages")
        return -1

def write_msg(socket:socket.socket, text, addr):
    msg = int(4).to_bytes() + int(ipaddress.ip_address(addr)).to_bytes(16) + len(text.encode()).to_bytes(2) + text.encode("utf-8")
    socket.send(len(msg).to_bytes(3)+msg)

    r = socket.recv(4)
    if r == bytes([255,255,255,255]):
        return 0
    print(r)
    return 1

def start_connect(socket: socket.socket):
    socket.send(int(3).to_bytes(3)+bytes([0]))
    if socket.recv(4) != bytes([255,255,255,255]):
        print("ошибка подключения")
        return

class Messenger(cmd.Cmd):
    
    def __init__(self, completekey: str = "tab", stdin = None, stdout = None) -> None:
        super().__init__(completekey, stdin, stdout)
        self.intro = "Welcome to JUNQ-Messenger CLI"
        self.prompt = ">>> "
        self.login = None
        self.raddr = None
        self.contacts = {}
        self.rcontacts = {}

        self.msgs_offset = 0

    def rprompt(self):
        if self.login:
            if self.raddr:
                # print()
                self.prompt = f"({self.login}) [{self.rcontacts[self.raddr]}] # "
            else:
                self.prompt = f"{self.login} $ "

    def do_add_contact(self, args):
        addr, name = args.split()
        try:
            ipaddress.ip_address(addr)
        except:
            print("неправильный формат ipv6", addr)
        self.contacts.update({name: addr})
        self.rcontacts.update({addr: name})

    def do_gmsgs(self, args):
        count = 10
        if args not in ("", None):
            try:
                count = int(args)
            except:
                ...
        n = get_messages(self.socket, count, self.msgs_offset, self.rcontacts)
        if n != -1:
            self.msgs_offset += n
        else:
            self.msgs_offset = 0


    def do_sdialog(self, args):
        try:
            self.raddr = self.contacts[args]
            self.rprompt()
        except:
            print("wrong format")
        
    def complete_sdialog(self, text, line, begidx, endidx):
        if not text:
            return list(self.contacts.keys())
        else:
            completions = [ f
                            for f in list(self.contacts.keys())
                            if f.startswith(text)
                            ]
        return completions

    def do_w(self, args):
        if self.raddr:
            r = write_msg(self.socket, args, self.raddr)
            if r != 0:
                print("ошибка")
        else:
            print("нужно указать получателя: setraddr ipv6")

    def do_login(self, args):
        a = args.split()
        if len(a) == 2:
            r = login(self.socket, a[0], a[1])
            if r == 0:
                self.login = a[0]
                self.rprompt()
            else:
                print("err login")
                return
        else:
            print("Err syntax: login {login} {password}")
            return
        


    def do_connect(self, args):
        """Connect to daemon"""
        self.login = None
        self.rprompt()
        addr,port = args.split(" ")
        
        try:
            taddr = ipaddress.ip_address(addr)
        except ValueError:
            print("аддресс хуета")
            return
        try:
            port = int(port)
            if port > 65537 or port < 1:
                raise
        except:
            print("порт хуета")
            return
        

        if type(taddr) == ipaddress.IPv6Address:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, 0)
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        
        self.socket.settimeout(10)
        try:
            self.socket.connect((addr, port))
        except:
            print("ошибка подключения")
            self.socket.close()
            return
        start_connect(self.socket)




    def do_q(self, args):
        """Quit from JUNQ-Messenger"""
        if self.socket:
            self.socket.close()
        return True


# 201:b8df:c6ab:409e:82e3:a7f9:c0a5:f3a5



def main():
    m = Messenger()
    try:
        m.cmdloop()
    except KeyboardInterrupt:
        print()
        exit()
    except Exception as e:
        print(e)
        main()
if __name__ == "__main__":
    from sys import argv


    main()
    
