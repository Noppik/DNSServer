import time
import pickle
import socket
import dnslib
import sys

dnscach = {}
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 53))
server_socket.settimeout(0)
server_receive_socket.settimeout(0)
time_start = time.time()
print("Server work")
try:
    try:
        with open('cache.txt', 'rb') as f:
            dnscach = pickle.load(f)
            rem = []
            for n in dnscach:
                for t in dnscach[n]:
                    s, end = dnscach[n][t]
                    if end < int(time.time()):
                        rem.append((n, t))
            for n, t in rem:
                del dnscach[n][t]
    except IOError:
        pass
    while True:
        try:
            data = None
            try:
                data, address = server_socket.recvfrom(1024)
            except OSError:
                pass
            if data:
                ans_rec = None
                ans = dnslib.DNSRecord.parse(data)
                reansw = []
                for que in ans.questions:
                    if que.qname in dnscach and que.qtype in dnscach[que.qname]:
                        s, end = dnscach[que.qname][que.qtype]
                        print('Record ' + str(que.qname) + ' type ' + str(que.qtype) + ' date ' + str(time.ctime(end)))
                        print("From cash:")
                        print(s)
                        reansw.append(que)
                    else:
                        print('Record ' + str(que.qname) + ' type ' + str(que.qtype))
                for que in reansw:
                    ans.questions.remove(que)
                if ans.questions:
                    ans_rec = ans
                if ans_rec:
                    try:
                        server = ('8.8.4.4', 53)
                        server_receive_socket.sendto(ans_rec.pack(), server)
                        print('Request ' + str(server[0]) + ":" + str(server[1]))
                    except OSError:
                        pass
        except OSError:
            pass
        try:
            data, address = server_receive_socket.recvfrom(1024)
            print('Answer ')
            ans = dnslib.DNSRecord.parse(data)
            print(ans)
            for que in ans.rr:
                if que.rname in dnscach:
                    dnscach[que.rname][que.rtype] = (que, int(time.time()) + que.ttl)
                else:
                    dnscach[que.rname] = {que.rtype: (que, int(time.time()) + que.ttl)}
        except OSError:
            pass
        if time.time() - time_start > 120:
            rem = []
            for n in dnscach:
                for t in dnscach[n]:
                    s, end = dnscach[n][t]
                    if end < int(time.time()):
                        rem.append((n, t))
            for n, t in rem:
                del dnscach[n][t]
            time_start = time.time()
        time.sleep(0.1)
except:
    pass
finally:
    server_socket.close()
    server_receive_socket.close()
    with open('cache.txt', 'wb') as f:
        pickle.dump(dnscach, f)
    time.sleep(1)
    sys.exit(0)
