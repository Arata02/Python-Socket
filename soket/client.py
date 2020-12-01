# クライアントを作成

import socket
import threading
import re
import sys
import struct
from typing import Optional

#IPアドレス
host = "127.0.0.1"

#ポート番号
port = 8080

endflag = 1

#数字をサーバに送信する
def game_start(s):
    print("ゲームが開始されました.\n")
    #サーバからの受信用スレッドを作成
    handle_thread = threading.Thread(target=handler, args=(s,), daemon=True)
    handle_thread.start()
    while  endflag > 0:

        number = 0
        exp_num = 0

        input_num = input().split()

        x = len(input_num)
        
        if x == 1:
            number = input_num[0]
        elif x == 2:
            number = input_num[0]
            exp_num = input_num[1]

        # print(input_num)

        # #送信用データをbyte型 に変換
        #w, x, y, z, a, bの順番でパックする
        data = struct.pack("BBBBBB", int(number),int(exp_num),0,0,0,0)
        
        # print(data)

        # 送信
        s.send(data)
        print('”{}”を送信しました.\n'.format(number))

    #スレッドの処理が終わるのを待つ
    handle_thread.join()


def end_game(point, other1, other2, other3, other4):
    global endflag
    endflag = 0
    print("\nゲームが終了しました.")  
    print("あなたの得点は{}です.\n".format(point))

    print("その他のクライアントの得点.")
    print("得点{}".format(other1))
    print("得点{}".format(other2))
    print("得点{}".format(other3))
    print("得点{}".format(other4))

    #ゲームが終了したら切断する
    remove_conection(endflag)


def remove_conection(endflag):
    if endflag == 0:
        print("[切断] 通信が切断されました.")
        print("Enterを押すと終了します.")
        s.close()
        sys.exit()


#サーバからメッセージを受信
def handler(s):
    while True:
        data = s.recv(6)
        recvdata = struct.unpack("BBBBBB", data)

        #print(recvdata)

        if recvdata[0] == 1:#判定を受け取ったら
            point = recvdata[1]
            print("\n得点{}\n".format(point))

            print("その他のクライアントの得点.")
            other1 = recvdata[2]
            print("得点{}".format(other1))
            other2 = recvdata[3]
            print("得点{}".format(other2))
            other3 = recvdata[4]
            print("得点{}".format(other3))
            other4 = recvdata[5]
            print("得点{}".format(other4))

        #ゲーム終了が送られてき時
        if recvdata[0] == 128:
            point = recvdata[1]
            other1 = recvdata[2]
            other2 = recvdata[3]
            other3 = recvdata[4]
            other4 = recvdata[5]

            break
    end_game(point, other1, other2, other3, other4)


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #サーバを指定
        s.connect((host, port))
        print("サーバに接続しました.")
        print("ゲームが開始されるまで少々お待ちください。\n")
        
        #受け取ったバイナリをbyte型に変換
        data = s.recv(6)
        recvdata = struct.unpack("BBBBBB", data)

        #ゲーム開始を受け取ったら
        if recvdata[0] == 0:
            try:
                game_start(s)
            except ValueError:                
                s.close()
                sys.exit()
            except OSError:
                s.close()
                sys.exit()
            finally:
                s.close()
                print("終了します.")