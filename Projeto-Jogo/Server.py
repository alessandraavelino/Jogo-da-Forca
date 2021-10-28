# Alessandra // Hacjesse // Matheus

import socket
from _thread import *
import sys
import random
clientsAtivo = 0
words = [
    'celular', 'banana', 'jogo', 'computador', 'redes',
    'carro', 'bicicleta', 'monitor', 'mesa', 'teclado',
    'gato', 'cachorro', 'livro', 'cafe', 'melancia'
]
games = []

class Game:
    word = ""
    gameString = ""
    incorrectGuesses = 0
    incorrectLetters = 0
    turn = 1
    lock = 0
    completou = False

    def __init__(self, word, num_players_requested):
        self.incorrectLetters = []
        self.lock = allocate_lock()
        self.word = word
        for i in range(len(word)):
            self.gameString += "_"
        if num_players_requested == 1:
            self.completou = True

    def getStatus(self):
        if self.incorrectGuesses >= 6:
            return 'You perdeu :('
        elif not '_' in self.gameString:
            return 'Você ganhou!!'
        else:
            return ''

    def guess(self, letter):
        if letter not in self.word or letter in self.gameString:
            self.incorrectGuesses += 1
            self.incorrectLetters.append(letter)
            return 'Incorreto!'
        else:
            gameString = list(self.gameString)
            for i in range(len(self.word)):
                if self.word[i] == letter:
                    gameString[i] = letter
            self.gameString = ''.join(gameString)
            return 'Correto!'

    def changeTurn(self):
        if self.turn == 1:
            self.turn = 2
        else:
            self.turn = 1


def Main():
    global clientsAtivo
    global words

    ip = 'localhost'
    port = 7777

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    print('Servidor iniciando em ' + ip + '| Port ' + str(port))

  
    try:
        s.bind((ip, port)) 
    except socket.error as e:
        print(str(e))
    s.listen(6)  



    while True:
        c, addr = s.accept()
        clientsAtivo += 1
        print("Uma conexão " + str(clientsAtivo) + " ativa de: " + str(addr))
        start_new_thread(clientThread, (c,))

def getGame(num_players_requested):
    if num_players_requested == 2:
        for game in games:
            if not game.completou:
                game.completou = True
                return (game, 2)
    if len(games) < 3:
        word = words[random.randint(0, 14)]
        game = Game(word, num_players_requested)
        games.append(game)
        return (game, 1)
    else:
        return -1

def clientThread(c):  
    global clientsAtivo
                                                          
    twoPlayerSignal = c.recv(1024).decode('utf-8')

    if twoPlayerSignal == '2':
        x = getGame(2)
        if x == -1:
            send(c, 'Servidor lotado')
        else:
            game, player = x
            send(c, 'Aguardando outros jogadores...')

            while not game.completou:
                continue
            send(c, 'Jogo iniciando')
            twoPlayerGame(c, player, game)

    else:
        x = getGame(1)
        if x == -1:
            send(c, 'Servidor lotado')
        else:
            game, player = x
            onePlayerGame(c, game)

def send(c, msg):
    packet = bytes([len(msg)]) + bytes(msg, 'utf8')
    c.send(packet)

def dados_do_game(c, game):
    msgFlag = bytes([0])
    data = bytes(game.gameString + ''.join(game.incorrectLetters), 'utf8')
    gamePacket = msgFlag + bytes([len(game.word)]) + bytes([game.incorrectGuesses]) + data
    c.send(gamePacket)

def twoPlayerGame(c, player, game):
    global clientsAtivo                                                  

    while True:
        while game.turn != player:
            continue
        game.lock.acquire()

        status = game.getStatus()
        if status != '':
            dados_do_game(c, game)
            send(c, status)
            send(c, "Game Over!")
            game.changeTurn()
            game.lock.release()
            break

        send(c, 'Sua vez!')

        dados_do_game(c, game)

        rcvd = c.recv(1024)
        letterGuessed = bytes([rcvd[1]]).decode('utf-8')

        send(c, game.guess(letterGuessed))

        status = game.getStatus()
        if len(status) > 0:
            dados_do_game(c, game)
            send(c, status)
            send(c, "Game Over!")
            game.changeTurn()
            game.lock.release()
            break

        send(c, "Aguardando vez...")
        game.changeTurn()
        game.lock.release()

    if game in games:
        games.remove(game)
    c.close()
    clientsAtivo -= 1


def onePlayerGame(c, game):
    global clientsAtivo

    while True:
        dados_do_game(c, game)

        rcvd = c.recv(1024)
        letterGuessed = bytes([rcvd[1]]).decode('utf-8')

        send(c, game.guess(letterGuessed))

        status = game.getStatus()
        if len(status) > 0:
            dados_do_game(c, game)
            send(c, status)
            send(c, "Game Over!")
            break
    games.remove(game)
    c.close()
    clientsAtivo -= 1



if __name__ == '__main__':
    Main()
