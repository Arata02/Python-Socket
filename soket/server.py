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

# 終了判定に用いるユーザ
user_judg = 0

# ユーザ毎の受信カウンタ
user_counter = []

# 終了する受信回数
end_counter = 3

# 0~255に収めるチェック変数
#checked = 0

# アタリとハズレの設定
hit = random.randint(0, 99)
blank = random.randint(0, 99)
if hit == blank:
    hit += 1
elif hit == 99:
    blank -= 1
elif hit == 0:
    blank += 1


# クライアントと接続を切る
def remove_conection(con, address):
    userid = clients.index((con, address))
    print("[切断]ユーザID{}".format(userid))
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
            global user_counter
            user_counter.append(0)
            userid = clients.index((con, address))
            print("[接続]ユーザID{}".format(userid))
            # ユーザーごとのポイント
            global point
            point.append(0)

        game_start()


# クライアントからデータを受信する
def handler(con, address):
    # ユーザIDの取得
    userid = clients.index((con, address))
    # 特定のユーザがendcounter回回答を送信したら終了する
    while user_counter[user_judg-1] < end_counter:
        try:
            # データを受け取る最大6byte
            data = con.recv(6)
            recvdata = struct.unpack("<BBBBBB", data)

            print("[受信]ユーザID{} が”{}”と入力しました。".format(userid, recvdata[0]))

            if recvdata[0] == hit:  # 当たりの時
                point[userid] += 10
                #check = point[userid]
                #if check > 255:
                    #check = 255
                #elif check < 0:
                    #check = 0
                x = judgment(point[userid])
                point[userid] = x
                print('ユーザID{} がアタリを引きました. ユーザID{}のポイント= {}'.format(
                    userid, userid, point[userid]))
            elif recvdata[0] == blank:  # ハズレの時
                point[userid] -= 10
                # check = point[userid]
                # if check > 255:
                #     check = 255
                # elif check < 0:
                #     check = 0
                # point[userid] = check
                x = judgment(point[userid])
                point[userid] = x
                print('ユーザID{} がハズレを引きました. ユーザID{}のポイント= {}'.format(
                    userid, userid, point[userid]))
            elif recvdata[0] != hit and recvdata[5] != blank:
                point[userid] -= 1
                # check = point[userid]
                # if check > 255:
                #     check = 255
                # elif check < 0:
                #     check = 0
                # point[userid] = check
                x = judgment(point[userid])
                point[userid] = x
                print("ユーザID{} がその他を引きました. ユーザID{}のポイント = {}".format(
                    userid, userid, point[userid]))

            for c in clients:
                c[0].sendto(get_senddata(con, address, 1, recvdata[0]), c[1])
            user_counter[userid] += 1

        except ConnectionResetError:
            remove_conection(con, address)
            break
        except struct.error:
            break
    end_game()

def judgment(point):
    check = point
    checked = 0
    if check > 255:
        check = 255
        checked = check
    elif check < 0:
        check = 0
        checked = check
    else:
        checked = check
    return checked

# ゲーム開始
def game_start():
    print('\nゲームを開始します.')
    # クライアント数を取得
    client_num = len(clients)
    # 終了判定に用いるユーザをランダム選択
    global user_judg
    user_judg = random.randint(1, client_num)
    print("終了判定はユーザID{}で行います.\n".format(user_judg))

    for c in clients:
        # スレッド処理開始
        handle_thread = threading.Thread(target=handler,
                                         args=(c[0], c[1]),
                                         daemon=True)
        handle_thread.start()
        c[0].sendto(get_senddata(c[0], c[1], 0, 0), c[1])

    handle_thread.join()

# ゲーム終了
def end_game():
    print("ゲームを終了します.")
    for c in clients:  # クライアントに終了を伝える
        c[0].sendto(get_senddata(c[0], c[1], 128, 0), c[1])


# 送信データを返す
# 判定時のみnumberを使用。それ以外の時は無視する。
def get_senddata(con, address, w_type, number):
    # ユーザIDを取得
    userid = clients.index((con, address))
    # クライアント数を取得
    clientnumber = len(clients)
    number = int(number)
    p = point[userid]

    w = w_type
    x = 0
    y = 0
    z = 0
    a = 0
    b = 0

    if w_type == 0:  # ゲーム開始
        print("開始")
        x = 0
        y = 0
        z = 0
        a = 0
        b = 0

    elif w_type == 1:  # 判定
        print("判定")
        x = p
        y = 0
        z = 0
        a = 0
        b = 0

    elif w_type == 128:  # ゲーム終了
        print("終了")
        x = p
        y = 0
        z = 0
        a = 0
        b = 0

    data = struct.pack("<BBBBBB", w, x, y, z, a, b)
    return data

if __name__ == "__main__":
    print("アタリ：{}, ハズレ：{}".format(hit, blank))
    server_start()
    print("ゲームを終了します.")