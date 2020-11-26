# クライアントを作成
import socket
import threading
import re
import sys
import struct

#IPアドレス
host = "127.0.0.1"

#ポート番号
port = 8080

endflag = 1

#数字をサーバに送信する
def game_start(s):
    print('ゲームが開始されました。')
    #サーバからの受信用スレッドを作成
    handle_thread = threading.Thread(target=handler, args=(s,), daemon=True)
    handle_thread.start()
    while  endflag > 0:
        print('数字を入力してください。')
        number = input()
        # #送信用データをリトルエンディアンでbyte型 に変換
        #data = struct.pack("<BBBB", 0,0,0,int(number))
        #w, x, y, z, a, bの順番
        data = struct.pack("BBBBBB", int(number),0,0,0,0,0)
        #送信
        print(data)
        s.send(data)
        print('”{}”を送信しました。\n'.format(number))

    #スレッドの処理が終わるのを待つ
    handle_thread.join()


def end_game(s, point):
    global endflag
    endflag = 0
    print('ゲームが終了しました。')
    
    print('あなたの得点は{}です。'.format(point))

    #ゲームが終了したら切断する
    remove_conection(s)


def remove_conection(s):
    print("[切断] 通信が切断されました.")
    print("Enterを押すと終了します.")
    s.close()
    sys.exit()


#サーバからメッセージを受信
def handler(s):
    while True:
        data = s.recv(6)
        recvdata = struct.unpack("BBBBBB", data)

        if recvdata[0] == 1:#判定を受け取ったら
            anyuserid = recvdata[1] + 1
            number = recvdata[2]
            point = recvdata[1]

            #print(recvdata)
            #print("[受信] 当たりを引きました.")
            print("貴方の得点{}".format(point))
            # print("その他を引きました.")
            # print("得点")
            #自身以外の判定の時
            # elif userid != anyuserid:
                    # print("[受信] 、ほかのユーザが”{}”と入力しました.".format(number))

        #ゲーム終了が送られてき時
        if recvdata[0] == 128:
            # rank = recvdata[2]
            point = recvdata[1]
           
            break
    end_game(s, point)


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #サーバを指定
        s.connect((host, port))
        print('サーバに接続しました。')
        print('ゲームが開始されるまで少々お待ちください。\n')

        #data = s.recv(4)
        #受け取ったバイナリをbyte型に変換
        #recvdata = struct.unpack("<BBBB", data)

        data = s.recv(6)
        recvdata = struct.unpack("BBBBBB", data)

        #ゲーム開始を受け取ったら
        if recvdata[0] == 0:
            try:
                userid = recvdata[1] + 1
                game_start(s)
            except ValueError:                
                s.close()
                sys.exit()
            except OSError:
                s.close()
                sys.exit()
            finally:
                s.close()
                print('終了します。')