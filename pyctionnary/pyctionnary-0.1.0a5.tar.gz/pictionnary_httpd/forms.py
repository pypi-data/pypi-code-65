from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class CreateRoomForm(FlaskForm):
    roomName = StringField('Room name', validators=[DataRequired()])
    maxScore = IntegerField("Maximum score (ending game when a player reaches it). 0 for infinite:", default=2000)
    maxRound = IntegerField("Maximum number of rounds. 0 for infinite :", default=3)
    maxTime = IntegerField("Game time length in minute.s 0 for infinite :", default=10)
    drawingTime = IntegerField("How much time a player has to draw (and others to guess) "
                               "in seconds. 0 for infinite  :", default=60)

    submit = SubmitField('Create room')


class ChosePlayerNameForm(FlaskForm):
    playerName = StringField('Your player name', validators=[DataRequired()])

    submit = SubmitField('Access room')