# socket サーバを作成
import socket
import threading
import random
import sys
import struct

# IPアドレス
host = "127.0.0.1"

# ポート番号
port = 8080

# 接続最大数
maxclient = 1

# クライアント情報
clients = []

# ポイント
point = []

# ゲーム終了に使うユーザ
particularuserid = 0

# ユーザーごとのコマンド受信回数
usercounter = []

# 終了する受信回数
endcounter = 3

# 1位のユーザーID
winuserid = 0

# 当たり
hit = random.randint(0, 99)
# ハズレ
blank = random.randint(0, 99)
# 当たりとハズレが同じ値だったらblankに+1する
# 当たりが9だったら1減らす
if hit == blank:
    hit += 1
elif hit == 99:
    blank -= 1
elif hit == 0:
    blank += 1


# クライアントと接続を切る
def remove_conection(con, address):
    userid = clients.index((con, address)) + 1
    print("[切断]ユーザID{}番".format(userid))
    con.close()
    clients.remove((con, address))


# サーバをスタートする
def server_start():
    # AF = IPv4 という意味
    # TCP/IP の場合は、SOCK_STREAM を使う
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # IPアドレスとポートを指定
        s.bind((host, port))
        # 接続
        s.listen(maxclient)
        # connection するまで待つ
        counter = 0
        while counter < maxclient:
            # クライアントと接続。返り値は2つ返ってくる
            con, address = s.accept()
            counter += 1
            # クライアントの情報をリストに格納
            global clients
            clients.append((con, address))
            # ユーザーごとの数字を送ってきた回数をリストに格納
            global usercounter
            usercounter.append(0)
            userid = clients.index((con, address)) + 1
            print("[接続]ユーザID{}番".format(userid))
            # ユーザーごとのポイント
            global point
            point.append(0)

        game_start()


# クライアントからデータを受信する
def handler(con, address):
    # ユーザIDの取得
    userid = clients.index((con, address)) + 1
    # 特定のユーザがendcounter回回答を送信したら終了する
    while usercounter[particularuserid-1] < endcounter:
        try:
            # データを受け取る最大6byte

            data = con.recv(6)
            recvdata = struct.unpack("<BBBBBB", data)

            print("[受信]ユーザID{}番が”{}”と入力しました。".format(userid, recvdata[0]))
            print(recvdata)
            
            if recvdata[0] == hit:  # 当たりの時
                point[userid-1] += 10
                print('ユーザID{}番が当たりを当てました。ユーザID{}番のポイント= {}'.format(
                    userid, userid, point[userid-1]))
            elif recvdata[0] == blank:  # ハズレの時
                point[userid-1] -= 10
                print('ユーザID{}番がハズレを当てました。ユーザID{}番のポイント= {}'.format(
                    userid, userid, point[userid-1]))
            elif recvdata[0] != hit and recvdata[5] != blank:
                point[userid-1] -= 1
                print("ユーザID{}がその他を引きました. ユーザID{}のポイント = {}".format(
                    userid, userid, point[userid-1]))

            for c in clients:
                c[0].sendto(get_senddata(con, address, 1, recvdata[0]), c[1])
            usercounter[userid-1] += 1

        except ConnectionResetError:
            remove_conection(con, address)
            break
        except struct.error:
            break
    end_game()


# ゲーム開始
def game_start():
    print('\nゲームを開始します')
    # クライアント数を取得
    clientnumber = len(clients)
    # 特定のユーザをランダムで決める
    global particularuserid
    particularuserid = random.randint(1, clientnumber)
    print('特定のユーザはユーザID{}番です。\n'.format(particularuserid))

    for c in clients:
        # スレッド処理開始
        handle_thread = threading.Thread(target=handler,
                                         args=(c[0], c[1]),
                                         daemon=True)
        handle_thread.start()
        c[0].sendto(get_senddata(c[0], c[1], 0, 0), c[1])

        print('senddata={}'.format(get_senddata(c[0], c[1], 0, 0)))

    handle_thread.join()


def end_game():
    global winuserid
    winuserid = point.index(max(point)) + 1
    # print('ゲームを終了します。')
    # print('優勝はユーザID{}番です。'.format(winuserid))
    for c in clients:  # クライアントに終了を伝える
        c[0].sendto(get_senddata(c[0], c[1], 128, 0), c[1])


# 送信データを返す
# 判定時のみnumberを使用。それ以外の時は無視する。
def get_senddata(con, address, wtype, number):
    # ユーザIDを取得
    userid = clients.index((con, address))
    # クライアント数を取得
    clientnumber = len(clients)
    # 当たりとの差
    hitdist = abs(hit - int(number))
    # ハズレとの差
    blankdist = abs(blank - int(number))
    number = int(number)
    p = point[userid-1]
    print(point)

    w = wtype
    x = 0
    y = 0
    z = 0
    a = 0
    b = 0

    if wtype == 0:  # ゲーム開始
        print("開始")
        x = 0
        y = 0
        z = 0
        a = 0
        b = 0

    elif wtype == 1:  # 判定
        print("判定")
        x = p
        y = number
        z = 0
        a = 0
        b = 0

    elif wtype == 128:  # ゲーム終了
        # 1位のユーザーID
        winuserid = point.index(max(point))
        # ユーザーのポイント
        userpoint = point[userid]
        # 降順に並び替える
        sortedpoint = sorted(point, reverse=True)
        # ユーザーの順位
        rank = sortedpoint.index(userpoint)
        x = p
        y = 0
        z = 0
        a = 0
        b = 0

    #data = struct.pack("<BBBB", w,x,y,z)
    data = struct.pack("<BBBBBB", w, x, y, z, a, b)
    return data

if __name__ == "__main__":
    print('当たり：{}, ハズレ：{}'.format(hit, blank))
    server_start()
    print('ゲームを終了します。')
    print('優勝はユーザID{}番です。'.format(winuserid))