from pictionnary_httpd import app, socketio
from flask import url_for
from flask_socketio import join_room, leave_room, emit
from collections import OrderedDict
import json
from enum import Enum
import random
import threading
import os
import time
import traceback

script_dir = os.path.dirname(__file__)
print(script_dir)

games = {}
with open(os.path.join(script_dir, "./var/liste.txt")) as f:
    wordList = f.readlines()
    wordList = [w.replace("\n", "") for w in wordList]


def findGameByPlayerWsId(wsId):
    for roomName, game in games.items():
        if game.getPlayerByWsId(wsId):
            return game


class GamePhase(Enum):
    INIT = "INIT"
    CHOSE = "CHOSE"
    DRAW = "DRAW"
    SCORE = "SCORE"
    END = "END"


class PlayerStatus(Enum):
    ACTIVE = "active"
    DISCONNECTED = "disconnected"


def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[
                             j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1  # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


class RepeatedTimer(object):
  def __init__(self, interval, function, *args, **kwargs):
    self._timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.kwargs = kwargs
    self.is_running = False
    self.next_call = time.time()
    self.start()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    if not self.is_running:
      self.next_call += self.interval
      self._timer = threading.Timer(self.next_call - time.time(), self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False


class Game:
    def __init__(self, roomName, roomUrl, maxScore, maxRound, maxTime, timePerDrawing):
        self.roomName = roomName
        self.roomUrl = roomUrl
        self.maxScore = maxScore
        self.maxRound = maxRound
        self.maxTime = maxTime
        self.timePerDrawing = timePerDrawing
        self.endDrawingTimer = None
        self.timeoutSecBeforeSkip = 30
        self.scoreTime = 10
        self.scoreInfos = {}
        self.players = OrderedDict()
        self.playersGuessed = {}
        self.startGuessTime = None
        self.currentDrawingSteps = []
        self.currentPhase = GamePhase.INIT
        self.words = wordList.copy()
        random.shuffle(self.words)
        self.currRound = 0
        self.currentPlayerIdx = -1 # Current player index that is chosing a word or drawing
        self.currentPlayerName = None # Current player name that is chosing a word or drawing
        self.currentWord = None # Word that the player chosed to draw
        self.availWords = None # List of words among which the user had to chose
        self.noChecks = True # Boolean used to disable some checks to allow vulnerabilities
        self.canPlayerTalkDrawing = False # TODO prevent player from talking when drawing if this is true

        self.notifyTimeThread = None # Thread used to send time remaining to players in drawing phase

    def broadcastPlayerEnters(self, player):
        emit('playerEnters', player.to_dict(), room=self.roomName, skip_sid=player.wsId)

    def broadcastDrawing(self, mouseX, mouseY, drawerWsId):
        player = self.getPlayerByWsId(drawerWsId)
        if player.isDrawing:
            emit('draws', {"x": mouseX, "y": mouseY}, room=self.roomName, skip_sid=drawerWsId)
            self.currentDrawingSteps.append({"event": "draws", "x": mouseX, "y": mouseY})

    def broadcastMouseup(self, wsId):
        emit('mouseup', room=self.roomName, skip_sid=wsId)
        self.currentDrawingSteps.append({"event": "mouseup"})

    def broadcastMessage(self, message, wsId):
        playerName = self.getPlayerByWsId(wsId).name
        app.logger.debug(f"Receive {message}. Message sender : {playerName} "
                         f"currentPlayerName : {self.currentPlayerName} playerGuessed : {self.playersGuessed}")
        if self.currentPhase == GamePhase.DRAW and self.currentPlayerName != playerName and \
                playerName not in self.playersGuessed:
            self.checkWordFound(message, playerName)
        if message == "reset":
            self.restart()
        elif self.currentWord is None or message.lower() != self.currentWord.lower():
            # TODO resend message to sender. Add message to player tchat only when received from server
            emit('receiveMessage', {"playerName": playerName, "content": message}, room=self.roomName, skip_sid=wsId)

    def checkWordFound(self, message, playerName):
        app.logger.debug(f"Player message : {message.lower()}, word to guess : {self.currentWord.lower()}")
        if message.lower() == self.currentWord.lower():
            self.playersGuessed[playerName] = time.time() - self.startGuessTime
            emit('receiveMessage', {"server": True, "content": "You guessed the word !"},
                 room=self.players[playerName].wsId)
            emit('receiveMessage', {"server": True, "content": f"Player {playerName} guessed the word."},
                 room=self.roomName, skip_sid=self.players[playerName].wsId)
            self.checkAllPlayerGuessed()
        elif levenshtein(message.lower(), self.currentWord.lower()) <= 2:
            emit('receiveMessage', {"server": True, "content": f"The word {message} is near !"},
                 room=self.players[playerName].wsId)

    def checkAllPlayerGuessed(self):
        playerNames = self.players.keys()
        playerNames = list(playerNames - [self.currentPlayerName])
        playerNames.sort()
        playerGuessed = list(self.playersGuessed.keys())
        playerGuessed.sort()
        if playerNames == playerGuessed:
            self.startScorePhase()

    def startScorePhase(self):
        if self.endDrawingTimer is not None:
            self.endDrawingTimer.cancel()
            self.endDrawingTimer = None
            self.notifyTimeThread.stop()

        nbPlayerToGuess = len(self.playersGuessed)
        self.playersGuessed = {k: v for k, v in sorted(self.playersGuessed.items(), key=lambda item: item[1])}
        scoreInfos = {}
        sumRemaining = 0

        if self.timePerDrawing != 0:
            scoreCalcDrawer = ""
            for p, timeUsed in self.playersGuessed.items():
                playerGuessPodium = list(self.playersGuessed.keys()).index(p)
                app.logger.debug(f"Player {p} was the {playerGuessPodium} to guess")
                remainingTime = round(self.timePerDrawing - timeUsed)
                sumRemaining += remainingTime
                scoreCalcDrawer += " + " + str(remainingTime)
                scoreAdded = remainingTime * (nbPlayerToGuess - playerGuessPodium)
                strScoreCalc = f"({self.timePerDrawing} - {round(timeUsed)}) x ({nbPlayerToGuess} - {playerGuessPodium})"
                app.logger.debug(f"Player {p} has scored {scoreAdded}")
                self.players[p].score += scoreAdded
                scoreInfos[p] = {"scoreAdded": scoreAdded, "scoreCalc": strScoreCalc,
                                 "totalScore": self.players[p].score}
            # score pour celui ou celle qui dessine : additionner les temps restants pour chaque joueur
            app.logger.debug(f"Player {self.currentPlayerName} has scored {sumRemaining}")
            self.players[self.currentPlayerName].score += sumRemaining
            scoreInfos[self.currentPlayerName] = {"scoreAdded": sumRemaining, "scoreCalc": scoreCalcDrawer,
                                                  "totalScore": self.players[self.currentPlayerName].score}
        else:
            for name, p in self.players.items():
                p.score += 1
                scoreInfos[name] = {"scoreAdded": 1, "totalScore": p.score, "scoreCalc": ""}

        self.scoreInfos = scoreInfos
        app.logger.debug("Start score phase")
        self.players[self.currentPlayerName].isPlaying = False
        self.playersGuessed = {}
        self.startGuessTime = None
        self.currentPlayerName = None
        self.currentWord = None
        self.currentPhase = GamePhase.SCORE
        socketio.emit(GamePhase.SCORE.value, scoreInfos, room=self.roomName)
        threading.Timer(self.scoreTime, self.initChoicePhase).start()


    @staticmethod
    def overlayMessage(message, room, skip_sid):
        socketio.emit("overlayMessage", message, room=room, skip_sid=skip_sid)

    @staticmethod
    def removeOverlayMessage(room, skip_sid):
        emit("removeOverlayMessage", room=room, skip_sid=skip_sid)

    def playerEnters(self, playerName, clientId):
        if playerName in self.players:
            if self.players[playerName].status == PlayerStatus.ACTIVE:
                emit("error", "Player with same name already active in room", room=clientId)
            elif self.players[playerName].status == PlayerStatus.DISCONNECTED:
                app.logger.debug(f"Player {playerName} reconnecting")
                self.players[playerName].wsId = clientId
                self.players[playerName].status = PlayerStatus.ACTIVE
                join_room(self.roomName, clientId)
                # Send initial information about the current room state to the re-joining player
                self.sendInitInfo(self.players[playerName].wsId)
                # Inform other players that a player is reconnecting
                emit("playerReconnects", playerName, room=self.roomName, skip_sid=clientId)
        else:
            self.addPlayer(playerName, clientId)
            join_room(self.roomName, clientId)

    def addPlayer(self, playerName, clientId):
        app.logger.debug("Creating new player...")
        player = Player(playerName, clientId)
        self.players[playerName] = player
        self.broadcastPlayerEnters(player)
        self.sendInitInfo(self.players[playerName].wsId)

    def sendInitInfo(self, dest):
        playersInfo = [self.players[name].to_dict() for name in self.players]
        initInfo = {"players": playersInfo, "drawing": self.currentDrawingSteps, "phase": str(self.currentPhase.name)}
        p = self.getPlayerByWsId(dest)

        # Inform the reconnecting player, if s.he is the drawers, the word that s.he is supposed to draw.
        if self.currentPhase == GamePhase.DRAW and p.name == self.currentPlayerName:
            initInfo["word"] = self.currentWord

        app.logger.debug("Send init infos " + json.dumps(initInfo) + " " + dest)
        emit('initInfo', initInfo, room=dest)

        if self.currentPhase == GamePhase.CHOSE:
            socketio.emit(GamePhase.CHOSE.value, {"currPlayer": self.currentPlayerName}, room=dest)
            if p.name != self.currentPlayerName:
                self.overlayMessage(f"Player {self.currentPlayerName} is chosing a word...", room=dest, skip_sid=None)
            else:
                # Sending to the player the list of word list in which he or she can chose.
                socketio.emit("wordList", self.availWords, room=dest)
        elif self.currentPhase == GamePhase.DRAW:
            # Notifying the reconnecting player that we are in DRAW phase and which player is drawing.
            emit(GamePhase.DRAW.value, self.currentPlayerName, room=dest)
        elif self.currentPhase == GamePhase.SCORE:
            socketio.emit(GamePhase.SCORE.value, self.scoreInfos, room=dest)
        elif self.currentPhase == GamePhase.END:
            socketio.emit(GamePhase.END.value, room=dest)

    def setPlayerReady(self, isReady, clientId):
        if self.currentPhase == GamePhase.INIT:
            p = self.getPlayerByWsId(clientId)
            p.ready = isReady
            app.logger.debug(f"Setting {p.name} ready state to {isReady}")
            emit('playerReady', {"isReady": isReady, "playerName": p.name}, room=self.roomName, skip_sid=clientId)
            if self.allPlayersReady():
                # TODO Init random word list and chose the first player
                # Notify users that we're entering the next phase : chosing a word
                self.initChoicePhase()
        else:
            p = self.getPlayerByWsId(clientId)
            app.logger.warning(f"Player {p.name} tells us he is ready but we are not in INIT phase. "
                               f"This is not supposed to happen")

    def initChoicePhase(self):
        words = self.words[0:3]
        del self.words[0:3]
        self.startChoicePhase(words)

    # Starting choice phase. Checks that the newly selected player is active. If not (disconnected), it
    # starts a callback to check some time later if it reconnects. If not, another player is selected.
    def startChoicePhase(self, words, changePlayer=True):
        if changePlayer:
            if self.currentPlayerIdx + 1 == len(self.players):
                app.logger.debug("End round")
                self.currRound += 1
                if self.currRound == self.maxRound:
                    app.logger.debug("End game")
                    # Start end game phase
                    self.startEndPhase()
                    return
            self.currentPlayerIdx = (self.currentPlayerIdx + 1) % len(self.players)

        currPlayer = list(self.players.items())[self.currentPlayerIdx][1]
        if currPlayer.status == PlayerStatus.DISCONNECTED:
            if not changePlayer:
                # The player that we were waiting didn't reconnect, trying same function with the next player
                app.logger.info(f"Player {currPlayer.name} didn't reconnect, continuing with the next player.")
                self.startChoicePhase(words)
            else:
                # The newly selected player is not connected. We will check later if it is reconnected.
                app.logger.info(f"Player {currPlayer.name} is not connected, waiting "
                                f"{self.timeoutSecBeforeSkip} to see if it reconnects.")
                threading.Timer(self.timeoutSecBeforeSkip, self.startChoicePhase,
                                args=[words], kwargs={"changePlayer": not changePlayer}).start()
        elif currPlayer.status == PlayerStatus.ACTIVE:
            app.logger.info(f"Starting choice phase. {currPlayer.name} will chose a word.")
            self.currentPhase = GamePhase.CHOSE
            currPlayer.isPlaying = True
            socketio.emit(GamePhase.CHOSE.value, {"currPlayer": currPlayer.name}, room=self.roomName)
            self.overlayMessage(f"Player {currPlayer.name} is chosing a word...", room=self.roomName, skip_sid=currPlayer.wsId)
            self.currentPlayerName = currPlayer.name
            self.availWords = words
            socketio.emit("wordList", words, room=currPlayer.wsId)
            self.currentDrawingSteps = []
            self.setAllPlayersNotDrawing()

    def wordChosed(self, word, clientId):
        if self.currentPhase == GamePhase.CHOSE:
            player = self.getPlayerByWsId(clientId)
            if self.players[self.currentPlayerName].wsId == clientId:
                # Not checking that the word is in the sent list.
                if self.noChecks:
                    self.currentWord = word
                    self.startDrawingPhase()
                elif word in self.availWords:
                    self.currentWord = word
                    self.startDrawingPhase()
                else:
                    app.logger.error(f"The chosed word is not in the list of words sent to the player. The list was"
                                     f"{self.availWords} and the chosed word is {word}")
            else:
                app.logger.error(f"Player {player.name} sent us the word she chosed but it should be "
                                 f"{self.currentPlayerName} who is chosing")
        else:
            app.logger.error(f"Received wordChosed but we are not in CHOSE phase. "
                             f"We are in {self.currentPhase.value} phase.")

    def startDrawingPhase(self):
        app.logger.info("Starting drawing phase.")
        self.currentPhase = GamePhase.DRAW
        self.players[self.currentPlayerName].isDrawing = True
        emit(GamePhase.DRAW.value, self.currentPlayerName, room=self.roomName)
        self.startGuessTime = time.time()
        if self.timePerDrawing != 0:
            self.endDrawingTimer = threading.Timer(self.timePerDrawing, self.startScorePhase)
            self.endDrawingTimer.start()
            self.notifyTimeThread = RepeatedTimer(1, self.sendTimeLeft) # auto-starts

    def setAllPlayersNotDrawing(self):
        for n, p in self.players.items():
            p.isDrawing = False

    def startEndPhase(self):
        self.currentPhase = GamePhase.END
        socketio.emit(GamePhase.END.value, room=self.roomName)
        for name, p in self.players.items():
            p.isDrawing = True
        socketio.emit('receiveMessage', {"server": True, "content": "Game is finished ! Type 'reset' if you want to restart "
                                                           "with same settings."},
             room=self.roomName)

    def sendTimeLeft(self):
        now = time.time()
        elapsed = now - self.startGuessTime
        timeRem = round(self.timePerDrawing - elapsed)
        socketio.emit("timeLeft", timeRem, room=self.roomName)

    def allPlayersReady(self):
        allReady = True
        for name, p in self.players.items():
            if not p.ready:
                allReady = False
                break
        return allReady

    def getPlayerByWsId(self, wsId):
        for playerName, player in self.players.items():
            if player.wsId == wsId:
                return player
        return None

    def disconnectPlayer(self, wsId):
        player = self.getPlayerByWsId(wsId)
        if player:
            player.status = PlayerStatus.DISCONNECTED
            if self.currentPhase == GamePhase.INIT:
                player.ready = False
            emit('playerDisconnects', player.name, room=self.roomName)

    def restart(self):
        self.currentPhase = GamePhase.INIT
        self.currentDrawingSteps = []
        self.currentPhase = GamePhase.INIT
        self.words = wordList.copy()
        random.shuffle(self.words)
        self.currentPlayerIdx = -1
        self.currentPlayerName = None
        self.currentWord = None
        self.availWords = None
        self.noChecks = True
        for n, p in self.players.items():
            p.reset()
        self.sendInitInfo(self.roomName)


class Player:
    def __init__(self, name, wsId):
        app.logger.debug(f"Creating new Player name : {name}, wsId : {wsId}")
        self.score = 0
        self.wsId = wsId
        self.name = name
        self.color = "black"
        self.status = PlayerStatus.ACTIVE
        self.ready = False
        self.isDrawing = True
        self.isPlaying = False
        self.canTalk = True

    def to_dict(self):
        d = {
            "name": self.name,
            "color": self.color,
            "status": self.status.value,
            "score": self.score,
            "ready": self.ready,
            "isDrawing": self.isDrawing,
            "isPlaying": self.isPlaying,
            "canTalk": self.canTalk
             }
        return d

    def to_json(self):
        return json.dumps(self.to_dict())

    def reset(self):
        self.score = 0
        self.color = "black"
        self.status = PlayerStatus.ACTIVE
        self.ready = False
        self.isDrawing = True


def createGame(roomName, maxScore=5000, maxRound=3, maxTime=0, timePerDrawing=60):
    if roomName not in games:
        games[roomName] = Game(roomName, url_for('joinRoom', roomName=roomName),
                               maxScore, maxRound, maxTime, timePerDrawing)
        return True
    else:
        return False

def addPlayerToGame():
    pass


def getWords(count):
    pass
