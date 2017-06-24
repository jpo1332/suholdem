#!/usr/bin/env python3
import random
import math
import csv
import ast
import copy
import sys
sys.path[0:0] = ['/Users/JackOHara/Desktop/code/Pythonprograms/Poker']
from pokergamehead import *
from loadprobs import *
from checkprobs import *

    
def betting_round(game1, session1, rounds, firstround=False):
        if session1.player1.allin == True or session1.secondplayer.allin == True:
            return
        game1.turn = session1.bblind
        game1.previousbet = 0
        session1.player1.potinvest = 0
        session1.secondplayer.potinvest = 0
        if firstround:
            game1.previousbet = session1.blindamount
            if session1.bblind:
                session1.player1.potinvest = session1.blindamount / 2
                session1.secondplayer.potinvest =  session1.blindamount
            else:
                session1.secondplayer.potinvest = session1.blindamount / 2
                session1.player1.potinvest = session1.blindamount
        session1.player1.active = True
        session1.secondplayer.active = True
        turn_function(session1, game1, game1.turn, rounds)
        #print "Pot:{0}   Player 1:{1}  Player 2:{2}".format(game1.pot, session1.player1.money, session1.secondplayer.money)
        return

def turn_function(session1, game1, turn, rounds):
        if turn == True:
            if session1.secondplayer.status == False:
                return
            if session1.player1.active == False:
                return
            if session1.player1.allin == True:
                return
            #print "Player 1:",

            move, _ = check_prob(rounds, game1, game1.player1)
                
            if move == 1:
                session1.player1.call(game1)
            if move == 2:
                session1.player1.raise1(game1, minimum_bet(session1.blindamount,0) + session1.blindamount, game1.previousbet)
                session1.secondplayer.active = True
            if move == 0:
                if session1.player1.potinvest >= game1.previousbet:
                    session1.player1.call(game1)
                else:
                    session1.player1.fold(game1)
            turn_function(session1, game1, not turn, rounds)
            return
        if turn == False:
            if session1.player1.status == False:
                return
            if session1.secondplayer.active == False:
                return
            if session1.secondplayer.allin == True:
                return
            #print "Player 2:",
            move, _ = check_prob(rounds, game1, game1.secondplayer)
            if move == 1:
                session1.secondplayer.call(game1)
            if move == 2:
                session1.secondplayer.raise1(game1, minimum_bet(session1.blindamount, 0) + session1.blindamount, game1.previousbet)
                session1.player1.active = True
            if move == 0:
                if session1.secondplayer.potinvest >= game1.previousbet:
                    session1.secondplayer.call(game1)
                else:
                    session1.secondplayer.fold(game1)
            turn_function(session1, game1, not turn, rounds)
            return
        return

def special_round(session1, game1, turn, rounds):
        if session1.player1.allin == True or session1.secondplayer.allin == True:
            return - 1
        game1.previousbet = 0
        session1.player1.potinvest = 0
        session1.secondplayer.potinvest = 0
        session1.player1.active = True
        session1.secondplayer.active = True
        if turn == False:
            if session1.player1.status == False:
                return -1 
            if session1.secondplayer.active == False:
                return -1 
            if session1.secondplayer.allin == True:
                return -1
            #print "Player 2:",
            #game1.river()
            move, _ = check_prob(rounds, game1, game1.secondplayer)
            if move == 1:
                session1.secondplayer.call(game1)
            if move == 2:
                session1.secondplayer.raise1(game1, minimum_bet(session1.blindamount, 0) + session1.blindamount, game1.previousbet)
                session1.player1.active = True
            if move == 0:
                if session1.secondplayer.potinvest >= game1.previousbet:
                    session1.secondplayer.call(game1)
                else:
                    session1.secondplayer.fold(game1)
            turn = not turn
        if turn == True:
            #print "Player 1:",
            if session1.secondplayer.status == False:
                return -1 
            if session1.player1.active == False:
                return -1 
            if session1.player1.allin == True:
                return -1
            winner = game1.compare_score(game1.secondplayer, game1.player1)
            optimum = [0, 1, 0]
            if (game1.player1.handscore.level + (game1.player1.handscore.type * .07))- (
                game1.secondplayer.handscore.level + (game1.secondplayer.handscore.type *.07)) >= .8:
                optimum = [0, 0, 1]
            if (game1.player1.handscore.level + (game1.player1.handscore.type * .07))- (
                game1.secondplayer.handscore.level + (game1.secondplayer.handscore.type *.07)) <= -1.2:
                optimum = [1, 0, 0]
            return optimum
            
        

def new_game(session1):
    a = game(session1)
    session1.player1.status = True
    session1.secondplayer.status = True
    session1.player1.allin = False
    session1.secondplayer.allin = False
    a.start(session1)
    betting_round(a, session1, 0, firstround=True)
    if end_round(a, session1):
        if session1.player1.status != True:
            return -1
        else:
            return -1
    a.flop()
    winner = a.compare_score(a.secondplayer, a.player1)
    tempscore = a.secondplayer.handscore.type + (a.secondplayer.handscore.level * .07)
    
    #inputs = return_variables(session1, a, a.secondplayer, 2)
    optimum = special_round(session1, a, session1.bblind, 2)
    if type(optimum) != list:
        return -1
    _, prob = check_prob(1, a, a.player1)
    high = return_highcard(a.secondplayer, a.community)
    a.community.update_score(0)
    difference = a.player1.handscore.type - a.community.handscore.type
    
    if a.player1.handscore.type < 15 and difference:
        difference = .5
    elif difference and a.community.handscore.type < 15:
        difference = a.player1.handscore.type - 14
    return [[prob , difference] + [session1.secondplayer.previousmove, session1.bblind] + optimum]
    

    
def return_variables(session1, game1, players, rounds):
    _, probability = check_prob(rounds, game1, players)
    return [probability, game1.pot, game1.previousbet]

tothands = 0

runs = 90000
rivernndata = open("flopnn2data.csv", 'w')
wr = csv.writer(rivernndata, dialect='excel')

turns = True
for x in range(runs):
    test = 0
    test2 = 0
    a = session(playerchips=400)
    a.bblind = turns
    tothands += 1
    output = new_game(a)
    if output != -1:
        if output[0][2] != -1:
            wr.writerows(output)

    turns = not turns
    if x % 5000 == 0:
        print "Run:", x
        
    
print tothands

print "Success"
