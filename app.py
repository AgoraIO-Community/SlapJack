from flask import Flask, render_template, request, url_for, redirect, Markup, jsonify, make_response, send_from_directory, session, send_file
import os
import random
import glob
import time


try:
	from keys import *
except:
	AGORA_KEY = os.environ.get('API_KEY', None)

ORDER = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

app = Flask(__name__, static_url_path='/static')
CARDS = glob.glob("static/cards/*")
ACTIVE_CARDS = CARDS
DEALT_CARDS = []
MOST_RECENT = []
LAST_SENT = []

@app.route('/', methods=['GET'])
def index():
	return render_template("index.html", API_KEY=AGORA_KEY)

@app.route('/recent', methods=["GET"])
def getMostRecent():
	while len(LAST_SENT) > 0:
		LAST_SENT.pop()
	if len(MOST_RECENT) == 0:
		getCard()
	file = MOST_RECENT[-1]
	return jsonify(file)

@app.route('/newCard', methods=["GET"])
def getCard():
	#print ACTIVE_CARDS
	a = random.choice(ACTIVE_CARDS)
	ACTIVE_CARDS.remove(a)
	filename = a
	info = {}
	info['file'] = filename
	info['time'] = int(time.time())
	MOST_RECENT.append(info)
	print MOST_RECENT
	#LAST_SENT.append(filename)
	return send_file(filename, mimetype='image/png')

@app.route('/reset', methods=["GET"])
def resetCards():
	print("CARDS HAVE BEEN RESET")
	while len(MOST_RECENT) > 0:
		MOST_RECENT.pop()
	while len(ACTIVE_CARDS) > 0:
		ACTIVE_CARDS.pop()
	while len(DEALT_CARDS) > 0:
		DEALT_CARDS.pop()
	for val in glob.glob("static/cards/*"):
		ACTIVE_CARDS.append(val)
	return jsonify({})

@app.route('/isNew', methods=["GET"])
def checkNew():
	try:
		return str(LAST_SENT[-1] != MOST_RECENT[-1]).lower()
	except Exception as exp:
		print exp
		return exp

def correctAnswer(playerID=None):
	while len(MOST_RECENT) > 0:
		MOST_RECENT.pop()

@app.route('/isWin', methods=["GET"])
def checkWin():
	if len(MOST_RECENT) < 2:
		return "False " + str(MOST_RECENT)
	else:
		tempList = sorted(MOST_RECENT, key=lambda k: k['time'])
		cardOne = tempList[-1]['file'].partition("/cards/")[2].partition(".png")[0][:-1]
		cardTwo = tempList[-2]['file'].partition("/cards/")[2].partition(".png")[0][:-1]
		cardOneIndex = ORDER.index(cardOne)
		cardTwoIndex = ORDER.index(cardTwo)
		if (cardTwoIndex == len(ORDER)-1) and (cardOneIndex == 0):
			correctAnswer()
			return "True"
		if cardOneIndex - cardTwoIndex == 1 or cardOne == cardTwo:
			correctAnswer()
			return "True"
	return "False" + str(MOST_RECENT)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
