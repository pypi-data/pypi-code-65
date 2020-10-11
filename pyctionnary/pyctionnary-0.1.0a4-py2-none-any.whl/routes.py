from pictionnary_httpd import app, socketio
from flask import render_template, redirect, url_for, request
from pictionnary_httpd.game import games
from pictionnary_httpd.forms import CreateRoomForm, ChosePlayerNameForm
from pictionnary_httpd.game import Game, Player, createGame, findGameByPlayerWsId

# Root page.
# Includes a form to create and parameter a new room
# Includes a list of available rooms to join them
@app.route('/', methods=['GET', 'POST'])
def index():
    print(games)
    roomUrls = {roomName: game.roomUrl for roomName, game in games.items()}

    form = CreateRoomForm()
    if form.validate_on_submit():
        chk = createGame(form.roomName.data, form.maxScore.data, form.maxRound.data,
                         form.maxTime.data, form.drawingTime.data)
        if chk is False:
            return "Couldn't create room : room name already used."
        app.logger.debug("Created room")
        return redirect(url_for('joinRoom', roomName=form.roomName.data))
    return render_template("home.html", roomUrls=roomUrls, form=form)


# Game room page
# Will redirect to username chosing page if no username is given in URL argument
# When a username is given, an HTML page serving the game (thus opening a websocket) is returned
@app.route('/room/<roomName>')
def joinRoom(roomName):
    playerName = request.args.get('playerName', default=None)
    app.logger.debug(f"Access {roomName}")
    if roomName not in games:
        return f"Error joining room. The room '{roomName}' does not exist"

    if playerName is None:
        return redirect(url_for('chosePlayerName', roomName=roomName))

    if playerName in games[roomName].players and games[roomName].players[playerName].status == "active":
        return f"Error joining room. The player '{playerName}' is already in the room and active"

    return render_template("game.html", playerName=playerName, roomName=roomName)


# Username chosing page. Clients normally reach this page when accessing a room without username.
# Includes a simple form with one input and a submit button
@app.route('/username/<roomName>', methods=['GET', 'POST'])
def chosePlayerName(roomName):
    form = ChosePlayerNameForm()
    if form.validate_on_submit():
        playerName = form.playerName.data
        return redirect(url_for('joinRoom', roomName=roomName) + "?playerName=" + playerName)

    return render_template("choseUsername.html", form=form)


# Received websocket message when a client enters a room.
# If the room exists, the user is added to it and other users are notified.
@socketio.on('join')
def wsJoinRoom(roomName, playerName):
    app.logger.debug('received ' + str(playerName) + " " + roomName + " " + request.sid)
    if roomName in games:
        games[roomName].playerEnters(playerName, request.sid)
    else:
        app.logger.error(f"Room name {roomName } does not exist")


@socketio.on('disconnect')
def disconnect():
    clientId = request.sid
    app.logger.debug(f"Disconnecting player with wsId {clientId}")
    game = findGameByPlayerWsId(clientId)
    game.disconnectPlayer(clientId)


@socketio.on('draws')
def receiveDraw(mouseX, mouseY):
    clientId = request.sid
    #app.logger.debug(f"Players with {clientId} draws")
    game = findGameByPlayerWsId(clientId)
    game.broadcastDrawing(mouseX, mouseY, clientId)

@socketio.on('wordChosed')
def receiveWord(word):
    clientId = request.sid
    app.logger.debug(f"Players with {clientId} chosed word {word}")
    game = findGameByPlayerWsId(clientId)
    game.wordChosed(word, clientId)

@socketio.on('mouseup')
def receiveMouseup():
    clientId = request.sid
    game = findGameByPlayerWsId(clientId)
    game.broadcastMouseup(clientId)


@socketio.on('sendMessage')
def receiveMessage(message):
    clientId = request.sid
    game = findGameByPlayerWsId(clientId)
    game.broadcastMessage(message, clientId)


@socketio.on('playerReady')
def setPlayerReady(isReady):
    clientId = request.sid
    game = findGameByPlayerWsId(clientId)
    game.setPlayerReady(isReady, clientId)
