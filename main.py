from requests import Session
from time import sleep 

s = Session()

def login(ip, s):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"
    }
    data = {
        "password": "admin",
        "username": "admin"
    }
    res = s.post(f"http://{ip}/api/login", headers=headers, json=data)
    try:
        return res.json()["success"]
    except:
        return

def checkPacketLoggingStatus(ip, s, fileName):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
        "X-XSRF-TOKEN": s.cookies.get_dict()["XSRF-TOKEN"]
    }
    res = s.get(f"http://{ip}/api/packet_capture_status", headers=headers)
    if res.status_code == 200:
        try:
            resJson = res.json()
            foundFileName = False
            for table in resJson:
                if table["filename"] == fileName and table["status"] == "completed":
                    return True
                elif table["filename"] == fileName:
                    foundFileName = True

            if foundFileName:
                return
            
            print(f"No packet logging job - {ip}")
            return False
        except:
            print(f"JSON table empty - {ip}")
            return None
    elif res.status_code == 401:
        print(f"Unauthorized - {ip}")
        return

def stopCommands(ip, s):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
        "X-XSRF-TOKEN": s.cookies.get_dict()["XSRF-TOKEN"]
    }
    data = {
        "msgType": 110
    }

    s.post(f"http://{ip}/api/stop-exec-command", data=data, headers=headers)

def startPacketLogging(ip, s, outPutFileName, duration):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
        "X-XSRF-TOKEN": s.cookies.get_dict()["XSRF-TOKEN"],
        "Content-Type": "application/json;charset=utf-8"
    }
    # Content length might be requred
    data = {
        "arguments":{
            "count": "0",
            "duration": str(duration),
            "filename": outPutFileName,
            "interface": "eth0",
            "size": "10",
            "snaplen": "0",
        },
        "command": "tcpdump",
        "msgType": 109,
    }
    stopCommands(ip, s)
    res = s.post(f"http://{ip}/api/exec-command", json=data, headers=headers)
    print(res.text)
    try:
        if res.json()["success"]:
            return True
        else:
            print("Packet logging not started.")
            return
    except:
        print("Packet logging not started.")
        return

def downloadPCAPfile(ip, s, fileName):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
        "X-XSRF-TOKEN": s.cookies.get_dict()["XSRF-TOKEN"]
    }

    res = s.get(f"http://{ip}/api/export-packet-capture?{fileName}", headers=headers)
    if res.status_code == 200:
        with open(f"{fileName}", "wb") as file:
            file.write(res.content)
        return True
    else:
        print(f"Failed to download pcap file - {ip}")
        return


# must add session as an argument for all functions 
# CLEAR ALL JOBS BEFORE COS IT WILL DOWNLOAD RANDOM FILE OR NOT DO TEST
# add support for multiple returns from checkpacketlogging status
# pcap START does not work
ip = "172.19.61.212"
fileName = "PCAPFILETESTING.pcap"
duration = 5

login(ip, s)
startPacketLogging(ip, s, fileName, duration)
sleep(duration)
check = checkPacketLoggingStatus(ip, s, fileName)
while check == False:
    sleep(2)
    check = checkPacketLoggingStatus(ip, s, fileName)
    if check == None:
        break
if not check:
    quit()
print(f"Downloading pcap file - {ip}")
downloadPCAPfile(ip, s, fileName)