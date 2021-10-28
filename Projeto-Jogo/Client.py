import socket
import sys

def Main():
    ip = 'localhost'
    port = 7777
    print('Client ativo em ' + ip + '| Port ' + str(port))

    s = socket.socket()
    s.connect((ip, port))
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    print("****B E M   -  V I N D O****")
    print("******      ao       *******")
    print("*******Jogo da Forca********")
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    print("Modo multiplayer? (s/n)")
    print(">>", end='')
    msg = input().lower()

    while 1:
        if msg == 's' or msg == 'n':
            break
        msg = input('Escolha uma opção s (Sim) ou n (Não)')

    if msg == 's':
        twoPlayerSignal = '2'.encode('utf-8')
        s.send(twoPlayerSignal)
        playGame(s)

    else:
        twoPlayerSignal = '0'.encode('utf-8')
        s.send(twoPlayerSignal)

        print("Um jogador iniciou uma partida")
        playGame(s)

def recv_helper(socket):
    first_byte_value = int(socket.recv(1)[0])
    if first_byte_value == 0:
        x, y = socket.recv(2)
        return 0, socket.recv(int(x)), socket.recv(int(y))
    else:
        return 1, socket.recv(first_byte_value)

def playGame(s):
    while True:
        pkt = recv_helper(s)
        msgFlag = pkt[0]
        if msgFlag != 0:
            msg = pkt[1].decode('utf8')
            print(msg)
            if msg == 'Servidor lotado' or 'Game Over!' in msg:
                break
        else:
            gameString = pkt[1].decode('utf8')
            incorrectGuesses = pkt[2].decode('utf8')
            print(" ".join(list(gameString)))
            print("Palpites incorreto: " + " ".join(incorrectGuesses) + "\n")
            if "_" not in gameString or len(incorrectGuesses) >= 6:
                continue
            else:
                letterGuessed = ''
                valid = False
                while not valid:
                    letterGuessed = input('Letra escolhida: ').lower()
                    if letterGuessed in incorrectGuesses or letterGuessed in gameString:
                        print("Erro! A letra " + letterGuessed.upper() + " Já foi escolhida antes, pense em outra opção.")
                    elif len(letterGuessed) > 1 or not letterGuessed.isalpha():
                        print("Erro! Escolha apenas uma letra")
                    else:
                        valid = True
                msg = bytes([len(letterGuessed)]) + bytes(letterGuessed, 'utf8')
                s.send(msg)

    s.shutdown(socket.SHUT_RDWR)
    s.close()


if __name__ == '__main__':
    Main()
