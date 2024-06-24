import json
import time
import subprocess
import pathlib



def launch(*args):
    pth = "./junqd"
    req_paths = [pth+"/",
                 pth+"/junq-daemon.conf",
#                 pth+"/junq-daemon",
                 pth+"/yggstack"]
    
    for i in req_paths:
        if not pathlib.Path(i).exists():
            print(i, "ERR")
            print("Err cant find required paths")
            exit()
    
    with open(pth+"/junq-daemon.conf") as file:
        jf = json.load(file)
    
    for user in jf["users"]:
        if not pathlib.Path(pth+"/"+user["login"]+".conf").exists():
            print(pth+"/"+user["login"]+".conf", "ERR")
            print("Err cant find required paths")
            exit()
    files = []
    prcss = []
    for user in jf["users"]:
        f = open(f"{user['login']}.log", "w")
        files.append(f)
        prcss.append(subprocess.Popen(f"./yggstack -useconffile {user['login']}.conf -socks :{user['ygg_proxy_port']} -exposetcp 1109:127.0.0.1:{user['socket_port']}".split(), cwd=pth, stdout=f, stderr=f))

    time.sleep(0.5)
    f = open("junq-daemon.log", "w")
 #   prcss.append(subprocess.Popen("./junq-daemon", cwd=pth, stdout=f, stderr=f))
    # a = subprocess.Popen("sleep 5".split())
    # a.
    # prcss.append(subprocess.Popen("sleep 5".split()))
    try:
        while True:
            for i in prcss:
                if i.poll() != None:
                    print("LAUNCHER ERR", i.args)
                    ext(prcss,files)
            time.sleep(2)
    except:
        ext(prcss,files)

def ext(prcss, files):
    for i in prcss:
        i.terminate()
    for i in files:
        i.close()
    exit()
        


if __name__ == "__main__":
    launch()
