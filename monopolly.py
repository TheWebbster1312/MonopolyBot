#=======================imports===============================
import random
import discord
import json
from discord.abc import PrivateChannel
#import request
from discord.appinfo import AppInfo
from discord.ext import commands, tasks
from itertools import cycle
from PIL import Image
from discord.utils import resolve_template
#=======================derfining variables and global Meathods===================
playerList = []

def bankrupcy(player, bankrupter):
    print(player.name, "is bankrupt")
    playerList.remove(player)
    if bankrupter == "bank":# unnasignes all of theyre proeprty 
        player.removeAllProperties()# will remove all of theyre properties and return to default
    else:
        for i in player.getProperties():
            bankrupter.payIn((i.houses*i.costOfHouse)/2)# pays th ebankrupter half of the value of the houses
            i.transferOwner(bankrupter)
def getPlayer(ctx, board):
    for i in board.playerList:
        if i.name == ctx.author.display_name:
            return i
    return None
def getPlayerFromName(display_name, board):
    for i in board.playerList:
        if i.name == display_name:
            return i
    return None
def getBoard(ctx):
    for i in games:
        if i.server.id == ctx.guild.id:
            return i
#=======================property class=======================
class PropertyCard:#add morgage
    def __init__(self,colour, siteValue, rentList, costOfHouse, name): #defining initial variables for houses.
        self.name = name
        self.colour = colour
        self.siteValue = siteValue
        self.rentList = rentList # rent will be a list ranging 0-5 where 0 is site rent and 1 is 1 house rent etc 5 is a hotel rent.
        self.costOfHouse = costOfHouse
        self.morgateValue = self.siteValue/2
        self.owner = "NotYetAssigned"
        self.houses = 0
        self.rent = self.rentList[self.houses]
        self.monopolized = False
        self.Mortgaged = False
    def assignOwner(self,newOwner):#sets the owner of the property, when they buy the property
        self.owner = newOwner
        self.owner.update(self)
        self.owner.payOut(self.siteValue)
    def transferOwner(self,newOwner):#sets the new owenr for free
        self.owner.removeProperty(self)
        speak(self.owner.private, f"You **Lost** **{self.name}**")
        self.owner = newOwner
        speak(self.owner.private, f"You **Gained** **{self.name}**")
        self.owner.update(self)
        self.houses = 0
    def updateRent(self): #will update the rent value based on houses owned
        self.rent = self.rentList[self.houses]
    def buyHouse(self):#adds a house === and error catching for unassigned owner and only upgrade them linearly
        if self.houses < 4:
            if self.monopolized:
                if self.canBuyHouse():
                    self.houses += 1
                    self.owner.payBank(self.costOfHouse)
                    self.updateRent()
                    speak(self.owner.general,f"<@{self.owner.member.id}> just bought house a **house** for **{self.name}**")
                    self.owner.board.updateBoardImageHouses(self)
                else:
                    speak(self.owner.general,f"<@{self.owner.member.id}>You must have all properties at the same number of house before you buy more")
            else:
                speak(self.owner.general,f"<@{self.owner.member.id}>You need to monopolize {self.colour} to buy a house first")
        else:
            print("too many houses")
    def sellHouse(self):#takes away a house
        if self.houses != 0:
            if self.canSellHouse():
                self.houses -= 1
                self.owner.payIn(int(self.costOfHouse/2))
                self.updateRent()
                speak(self.owner.general,f"<@{self.owner.member.id}> just sold house a **house** for **{self.name}**")
                self.owner.board.updateBoardImageHouses(self)
                self.owner.announceMoneyUpdate("in", int(self.costOfHouse/2), f"for selling a house on **{self.name}**")
            else:
                speak(self.owner.general,f"<@{self.owner.member.id}>You must have all properties at the same number of house before you sell more")
        else:
            speak(self.owner.general, "You cannot sell any more houses on this property")

    def monopolize(self):
        self.monopolized = True
        if self.houses == 0:
            self.rent = self.rent*2
    def deMonopolize(self):
        self.monopolized = False
        if self.houses == 0:
            self.rent = self.rentList[0]
    def mortgage(self):
        if self.Mortgaged == False:
            self.Mortgaged = True
            self.owner.properties[self.colour].remove(self)
            self.owner.mortgaged.append(self)
            self.owner.payIn(self.morgateValue)
            speak(self.owner.general, f"{self.owner.name} just morgated {self.name}")
            self.owner.announceMoneyUpdate("In", self.morgateValue, f"for mortgaging {self.name}")
        else:
            speak(self.owner.general, "Already mortgaged")
    def deMorgage(self):
        if self.Mortgaged == True:
            self.Mortgaged = False
            self.owner.mortgaged.remove(self)
            self.owner.properties[self.colour].append(self)
            self.owner.payBank(int(self.morgateValue+self.morgateValue*0.1))
            speak(self.owner.general, f"{self.owner.name} just demorgated {self.name}")
            self.owner.announceMoneyUpdate("Out", self.morgateValue, f"for demortgaging {self.name}")
        else:
            speak(self.owner.general, "Already demortgages")
    def canBuyHouse(self):
        # make sue other houses of same colour are no more than +-1 house from the rest
        #the most can only be 1 greater than the least
        #the least can only be 1 less than the most
        ifHappened = self.houses+1# this is used to check what the outcome would be if a house were bought
        most = ifHappened
        least = ifHappened
        for i in self.owner.properties[self.colour]:
            if isinstance(i, int) or i == self:# skips the number in the list and itself
                continue
            if i.houses < least:
                least = i.houses
            elif i.houses > most:
                most = i.houses
        if most-least <= 1:
            return True
        else:
            return False
    def canSellHouse(self):
        # make sue other houses of same colour are no more than +-1 house from the rest
        #the most can only be 1 greater than the least
        #the least can only be 1 less than the most
        ifHappened = self.houses-1# this is used to check what the outcome would be if a house were bought
        most = ifHappened
        least = ifHappened
        for i in self.owner.properties[self.colour]:
            if isinstance(i, int) or i == self:# skips the number in the list and itself
                continue
            if i.houses < least:
                least = i.houses
            elif i.houses > most:
                most = i.houses
        if most-least <= 1:
            return True
        else:
            return False
def sumUp(self):
        if self.owner == "NotYetAssigned":
            name = "not owned"
        else:
            name = self.owner.name
        sumUp = [f"```\n=======Deeds for {self.name}=======",
                f"Colour: {self.colour}",
                f"Site Value: £{self.siteValue}",
                "===Rent===",
                f"Site Rent: £{self.rentList[0]}",
                f"1 House: £{self.rentList[1]}",
                f"2 Houses: £{self.rentList[2]}",
                f"3 Houses: £{self.rentList[3]}",
                f"4 Houses: £{self.rentList[4]}",
                f"1 Hotel: £{self.rentList[5]}",
                "===Houses and Hotels===",
                f"House : £{self.costOfHouse}",
                f"Hotel : 4 Houses + £{self.costOfHouse}",
                f"Current Owner: {name}",
                "```"]
        return "\n".join(sumUp)
#=======================transport cards===================
class TransportCard:
    def __init__(self, name):
        self.name = name
        self.siteValue = 200
        self.colour = "transport"
        self.owner = "NotYetAssigned" 
        self.rentList = [0,25,50,100,200]
        
    def assignOwner(self, newOwner):
        self.owner = newOwner
        self.owner.update(self)
        self.owner.payOut(self.siteValue)
        self.updateRent()
        self.updateOtherRent()
    def transferOwner(self,newOwner):#sets the new owenr for free
        self.owner.removeProperty(self)
        speak(self.owner.private, f"You **Lost** **{self.name}**")
        self.owner = newOwner
        speak(self.owner.private, f"You **Gained** **{self.name}**")
        self.owner.update(self)
    def updateRent(self):
        self.rent = self.rentList[len(self.owner.properties["transport"])]
    def updateOtherRent(self):
        for i in self.owner.properties["transport"]:
            if i != self: i.updateRent()
    def sumUp(self):
        name = self.owner.name if self.owner == "NotYetAssigned" else "Not Owned"
        sumUp = [f"```\n=======Deeds for {self.name}=======",
                f"Type: {self.colour}",
                f"Site Value: £{self.siteValue}",
                "===Rent===",
                f"1 Transport owned: £{self.rentList[0]}",
                f"2 Transports owned: £{self.rentList[1]}",
                f"3 Transports owned: £{self.rentList[2]}",
                f"4 Transports owned: £{self.rentList[3]}",
                f"Current Owner: {name}",
                "```"]
        return "\n".join(sumUp)
#=======================utility cards===================
class UtilityCard:
    def __init__(self, name):
        self.name = name
        self.siteValue = 150
        self.colour = "utility"
        self.owner = "NotYetAssigned"
        
    def assignOwner(self, newOwner):
        self.owner = newOwner
        self.owner.update(self)
        self.owner.payOut(self.siteValue)
    def transferOwner(self,newOwner):#sets the new owenr for free
        self.owner.removeProperty(self)
        speak(self.owner.private, f"You **Lost** **{self.name}**")
        self.owner = newOwner
        speak(self.owner.private, f"You **Gained** **{self.name}**")
        self.owner.update(self)

    def updateRent(self, roll):
        if len(self.owner.properties["utility"]) < 2:
            self.rent = 4*roll
        else:
            self.rent = 10*roll
    def sumUp(self):
        if self.owner == "NotYetAssigned":
            name = "not owned"
        else:
            name = self.owner.name
        sumUp = [f"```\n=======Deeds for {self.name}=======",
                f"Type: {self.colour}",
                f"Site Value: £{self.siteValue}",
                "===Rent===",
                f"1 Utility owned: 4 x Players roll",
                f"2 Utility owned: 10 x Players roll",
                f"Current Owner: {name}",
                "```"]
        return "\n".join(sumUp)
#======================community/chance Cards====================
class CommunityCard:
    def __init__ (self, Type, value, name, customFunc=lambda:None):
        self.name = name
        self.value = value
        self.Type = Type
        self.customFunc = customFunc
    def takeFromAll(self,amount,reciving):
        for i in playerList:
            i.payPlayer(reciving, amount)
    def activate(self, player):
        #important becasue it has the player it will be effecting
        if self.Type == "payOut": 
            player.payBank(self.value)
        elif self.Type == "payIn": 
            player.payIn(self.value)
        elif self.Type == "takeFromAll": 
            self.takeFromAll(self.value, player)
        elif self.Type == "forwardsSet": 
            if self.value - player.place > 0: 
                player.moveForward(self.value-player.place) 
            else: 
                player.moveForward(self.value - player.place+40)
        elif self.Type == "backwardsSet": 
            player.moveBackward(player.place-self.value)
        elif self.Type == "move":
            if self.value > 0: 
                player.moveForward(self.value)
            else: 
                player.moveBackward(self.value) 
        elif self.Type == "getOut": 
            player.getOutOfJailFree += 1
        elif self.Type == "jail": 
            player.goesToJail()
        else: 
            print("error, please select valid card", self.Type)
        self.customFunc()
#=======================player class=======================
class Player:
    def __init__(self, name, cash, member = None, private = None, category = None, general = None, board=None, symbol=None):
        self.name = name
        self.cash = cash
        self.inJail = False
        self.turnsSpentInJail = 0
        self.getOutOfJailFree = 0
        self.place = 0
        self.lastRoll = 0
        self.rollValue = [0,0]
        self.private = private
        self.category = category
        self.general = general
        self.member = member
        self.board = board
        self.status = None
        self.symbol = symbol

        self.propertiesDefault = {#this is here to allow the properties to be completely wiped and reset
            "pink":[3],
            "darkBlue":[2],
            "lightBlue":[3],
            "green":[3],
            "yellow":[3],
            "orange":[3],
            "red":[3],
            "brown":[2],
            "transport":[],
            "utility":[]
        }
        self.properties = {#first indent is maximum number of properties. when the length-1 equals that number then they have a monopolly
            "pink":[3],
            "darkBlue":[2],
            "lightBlue":[3],
            "green":[3],
            "yellow":[3],
            "orange":[3],
            "red":[3],
            "brown":[2],
            "transport":[],
            "utility":[]
        }

        self.monopolys = []
        self.mortgaged = []

    def roll(self):
        self.rollValue = [random.randint(1,6), random.randint(1,6)]
        self.lastRoll = self.rollValue[0]+self.rollValue[1]
        if self.inJail == True:
            if self.rollValue[0] == self.rollValue[1]:
                speak(self.general, f":game_die:========**Dice Roll**========:game_die:\n<@{self.member.id}> rolled a **{self.rollValue[0]}** and a **{self.rollValue[1]}**\nYou **Rolled a double**. You get out of Jail")
                self.getOutOfJail()
            else:
                speak(self.general, f":game_die:========**Dice Roll**========:game_die:\n<@{self.member.id}> rolled a **{self.rollValue[0]}** and a **{self.rollValue[1]}**\nYou need to roll a double to get out of jail.")
        else:
            speak(self.general, f":game_die:========**Dice Roll**========:game_die:\n<@{self.member.id}> rolled a **{self.rollValue[0]}** and a **{self.rollValue[1]}**\nTotal: **{self.lastRoll}**")
    def payOut(self, amount):#the player pays the amount
        self.cash = self.cash-amount
        if self.cash <= 0:
            self.board.bankcruptcy(self)
    def payIn(self, amount):#the player gets the amount
        self.cash = self.cash+amount
    def announceMoneyUpdate(self, direction, amount, reason = ""):  
        tmplist = [f":dollar:===== Money {direction} =====:dollar:",
                    f"Paid: **£{amount}** {reason}",
                    f"Remaining: **£{self.cash}**"]
        speak(self.private,"\n".join(tmplist))
    def update(self, property):
        self.properties[property.colour].append(property)
        if(self.properties[property.colour][0] == len(self.properties[property.colour])-1):#if the player has all the cards of that colour
            self.newMonopoly(property)
    def removeProperty(self, property):# removes the property
        self.properties[property.colour].remove(property)
        if property.colour in self.monopolys:
            self.removeMonopoly(property)
    def removeAllProperties(self):
        self.properties = self.propertiesDefault
    def buyHouse(self, location):
        location.buyHouse()
    def newMonopoly(self, property):#doubles rent and adds colout to players monopolys
        self.monopolys.append(property.colour)
        for i in self.properties[property.colour]:
            if isinstance(i,int):# checks if its an intager and skips
                continue
            i.monopolize()
    def removeMonopoly(self, property):
        self.monopolys.remove(property.colour)
        for i in self.properties[property.colour]:
            if isinstance(i,int):# checks if its an intager and skips
                continue
            i.deMonopolize()
    def buyProperty(self,property):
        if property.owner == "NotYetAssigned":# if the house isnt owned
            property.assignOwner(self)
            self.announceMoneyUpdate("Out",property.siteValue, f"for **{property.name}**")
            speak(self.general,f"<@{self.member.id}> just bought **{property.name}**")
            self.board.updateBoardImageHouses(property)
        else:
            speak(self.general, f"<@{self.member.id}>You cannot buy **{property.name}**, **{property.owner.name}** already owns it")
    def payRent(self, property):
        if property.colour == "utility": property.updateRent(self.lastRoll)# calculates rent based on roll
        if property in property.owner.mortgaged:
            speak(self.genral, "this property is mortgaged and you dont have to pay rent")
        else:
            if property.rent > self.cash:
                bankrupcy(self, property.owner)
            else:
                self.cash -= property.rent
                property.owner.giveRent(property.rent)
                self.announceMoneyUpdate("Out",property.rent, f"for **Rent** to **{property.owner.name}**")
    def giveRent(self, amount):
        self.cash += amount
        self.announceMoneyUpdate("in", amount, "for **Rent**")
    def payBank(self,value):
        if value > self.cash:
            self.payOut(self.cash)
            bankrupcy(self, "bank")
        else:
            self.payOut(value)
            self.announceMoneyUpdate("Out",value, f" to the Bank")
    def payPlayer(self,player,value):
        self.cash -= value
        player.payIn(value)
        self.announceMoneyUpdate("Out",value,f" to **{player}**")
    def goesToJail(self):
        self.inJail = True
        self.place = 10
        self.board.sendToJail(self)
        speak(self.general, "f<@{self.member.id} Has been sent to Jail>")
    def getsOutOfJail(self):
        self.inJail = False
        self.board.getOutOfJail(self)
    def moveForward(self, value):
        self.place += value
        if self.place > 39:
            self.place = self.place - 39
            self.payIn(200)
            self.announceMoneyUpdate("In",200, f" for Salary")
        speak(self.general, f"<@{self.member.id}> Moved foreward **{value}**\nThey landed on **{self.place}: {self.board.getPlaceName(self.place)}**")
    def moveBackward(self, value):
        self.place -= value
        if self.place < 1:
            self.place = 40 + self.place
    def getProperties(self):
        self.propertyList = []
        for i in self.properties:
            for j in self.properties[i]:
                if isinstance(j, int):
                    continue
                self.propertyList.append(j)
        return self.propertyList
    def getPropertyNames(self):
        return list(map(lambda x: x.name, self.getProperties()))
    def sumUp(self):
        sumUp = [f"\n=======Overview {self.name}=======",
                f"Cash: £{self.cash}",
                f"Current Position: {self.place}",
                "===Properties===",
                "\n".join([f"    {self.board.Deck.index(x)}-"+x.colour +": "+x.name+str(("; Houses: "+str(x.houses)) if isinstance(x,PropertyCard) else "")+(str("; Rent: £"+str(x.rent))) for x in self.getProperties()]),
                "===Mortgaged Properties===",
                "\n".join([f"    {self.board.Deck.index(x)}-"+x.colour +": "+x.name+str(("; Houses: "+str(x.houses)) if isinstance(x,PropertyCard) else "")+(str("; Rent: £"+str(x.rent))) for x in self.mortgaged]),
                "===Monopolys===",
                "\n".join(["    -"+x for x in self.monopolys]),
                "===Jail Status===",
                f"In Jail: {self.inJail}",
                f"Get put of Jail free cards: {self.getOutOfJailFree}"
                ""]
        return "\n".join(sumUp)
#=======================creating game cards=================

#====transport cards 4

ChungusExpress = TransportCard("The Chungus Express")
PogAir = TransportCard("Poggers Airways")
EuropaBus = TransportCard("The Europa Bus Station")
BigDipper = TransportCard("The Intergalactic Big Dipper")


#===== utility cards 2

DiscordNitro = UtilityCard("Discord Nitro Subscription")
SpotifyPremium = UtilityCard("Spotify Premuim Membership")

#===== Pink Street 3
MawhinneyGardens = PropertyCard("pink",140,[10,50,150,450,625,750],100,"Mawhiney Gardens")
LiquorStreet = PropertyCard("pink",140,[10,50,150,450,625,750],100,"Liquor Street")
BrewDogBoulevard = PropertyCard("pink",160,[12,60,180,500,700,900],100,"BrewDog Boulevard")
#====== Dark blue Street 2
BoulderWorld = PropertyCard("darkBlue", 400, [50,200,600,1400,1700,2000],200, "Boulderworld Belfast")
HotRocks = PropertyCard("darkBlue", 350, [35,175, 500,1100,1300,1500],200, "HotRocks Tollymore")
#====== Light Blue Street 3
SmokingAlley = PropertyCard("lightBlue", 100, [6,30,90,270,400,550], 50, "The Smoking alley")
TheGreenRoom = PropertyCard("lightBlue", 100, [6,30,90,270,400,550], 50, "The Green Room")
Wellington = PropertyCard("lightBlue", 120, [8,40,100,300,450,600], 50, "Wellington Colledge Belfast")
#====== Green street 3
TheParlour = PropertyCard("green", 300, [26, 130, 390, 900, 1100, 1275], 200, "The Parlour")
ThompsonsGrarage = PropertyCard("green", 300, [26, 130, 390, 900, 1100, 1275], 200, "Thompsons Garage")
TheLongfellow = PropertyCard("green", 320, [28,150,450,1000,1200,1400], 200, "The LongFellow")
#====== Yellow Street 3
Medows = PropertyCard("yellow",260,[22,110,330,800,975,1150], 150,"The lagan Medows")
BelvoirForrest = PropertyCard("yellow",260,[22,110,330,800,975,1150], 150,"Belvoir Forrest")
Botanic = PropertyCard("yellow",280,[24,120,360,850,1025,1200], 150,"Botanic Gardens")
#===== Orange Street 3
JessicasStudio = PropertyCard("orange",200,[16,80,220,600,80,1000], 100,"Gibson Studios")
Ellies = PropertyCard("orange",180,[14,70,200,550,750,950], 100,"Ellie's Dungeon")
RakibsHouse = PropertyCard("orange",180,[14,70,200,550,750,950], 100,"Bangor Curry House")
#===== Red street 3
TheCanteena = PropertyCard("red",240,[20,100,300,750,925,1100],150,"The Canteena")
HothHotel = PropertyCard("red",220,[18,90,250,700,875,1050],150,"The Hotel of Hoth")
TheRazorCrest = PropertyCard("red",220,[18,90,250,700,875,1050],150,"The Razor Crest")
#===== Brown 2
ShitCreak = PropertyCard("brown",60,[2,10,30,90,160,250],50,"Shits Creak")
APaddle = PropertyCard("brown",60,[4,20,60,180,320,450],50,"A Paddle")
PropertyCardDeck = {#ordered deck where each card corrisponds to the board
1:ShitCreak,
3:APaddle,
5:ChungusExpress,
6:SmokingAlley,
8:TheGreenRoom,
9:Wellington,
11:MawhinneyGardens,
12:DiscordNitro,
13:LiquorStreet,
14:BrewDogBoulevard,
15:PogAir,
16:JessicasStudio,
18:Ellies,
19:RakibsHouse,
21:TheCanteena,
23:HothHotel,
24:TheRazorCrest,
25:EuropaBus,
26:Medows,
27:BelvoirForrest,
28:SpotifyPremium,
29:Botanic,
31:TheParlour,
32:ThompsonsGrarage,
34:TheLongfellow,
35:BigDipper,
37:HotRocks,
39:BoulderWorld
}
PropertyNameDeck = [str(PropertyCardDeck[x].name) for x in PropertyCardDeck]# just the names
#===========community chests

class CommunityCardDeck:
    def __init__(self, cards):
        self.cards = cards
        self.tmpDeck = []# just here to hold the cards while being shuffeled
    def cardShuffell(self):
        self.tmpDeck = []
        for _ in range(len(self.cards)):
            self.card = self.cards[random.randint(1,len(self.cards))-1]
            self.tmpDeck.append(self.card)
            self.cards.remove(self.card)
        self.cards = self.tmpDeck
    def listCards(self):
        for i in self.cards:
            print(i.type)
    def randomCard(self):#chooses the top card and puts it to the back
        self.card = self.cards[0]
        self.cards.remove(self.card)
        self.cards.append(self.card)
        return self.card


CommunityCards = CommunityCardDeck([
    #paid out
    CommunityCard("payOut", 50, "Only Fans Payment, Cough up £50, Simp"),
    CommunityCard("payOut", 50,  "You buy someone dinner who doesnt love you. Pay £50"),
    CommunityCard("payOut", 10, "5 shots of sambuka for me and all my friends. £10", ),
    CommunityCard("payOut", 100, "Brewdog investment gone bad, you loose £100 and your pride."),
    #paid in
    CommunityCard("payIn", 50, "Your on the side feet buisness is booming. £50"),
    CommunityCard("payIn", 20, "You have found £20 in another mans wallet. Finders keepers I guess."),
    CommunityCard("payIn", 10, "Darnell makes good on the 10er he owed you a long time ago, He regrets being dickhead"),
    CommunityCard("payIn", 100, "You Win a butterfly knofe in a CS:GO case. £100"),
    CommunityCard("payIn", 25, "You succeed in minor tax evasion. You cheeky dog. £25"),
    CommunityCard("payIn", 100, "Here mate, buy yourself something nice, £100 on me."),
    CommunityCard("payIn", 100, "Markiplier donates to your live stream, Good job Gamer! £100"),
    CommunityCard("payIn", 200, "You suceed in major tax evasion, £200 is now yours, unbeknown to HMRC"),
    CommunityCard("takeFromAll", 10, "Its your Birthday, take £10 from each player"),#10 from each player
    #move foreard
    CommunityCard("forwardsSet", 0, "move foreward to Go! Collect 200"),
    #move backwards
    CommunityCard("backwardsSet", 2, "move backwards to ShitsCreak"),# update place name dynamically
    #jail
    CommunityCard("getOut", 1, "Get out of jail free card! This can be saved for later."),
    CommunityCard("jail", 1, "Go to jail, Or pay £50 to get out")
])
ChanceCards = CommunityCardDeck([   
    #payout
    CommunityCard("payOut", 15, "You slurge on a tastey sandwich, £15"),
    CommunityCard("payOut", 20,  "Your Neighbour is strapped for cash and generosity takes the better of you, Loose £20"),
    #CommunityCard("payHouses", , "5 shots of sambuka for me and all my friends. £10", ),# per hotel house etc
    CommunityCard("payOut", 150, "Your cat gets stuck in the waching machine and it turns on. You need a new washing machine, loose £150"),
    #CommunityCard("payHouses", , "Brewdog investment gone bad, you loose £100 and your pride."),#per hosue hotel etc
    #payin
    CommunityCard("payIn", 150, "You manage to find your friends dog that had been missing\nYou swindle him for £150 for the location, Not a bad day."),
    CommunityCard("payIn", 100, "You go to a local dentists office and check inbetween the cussions, You find £100"),
    CommunityCard("payIn", 50, "You find a cup beside a homeless person that has passed out\nAwsome, theres £50 in it"),
    #go foreward
    CommunityCard("forwardsSet", 0, "move forewardto Go! Collect 200"),
    CommunityCard("forwardsSet", 40, "move foreward to ..."),# add last square name
    CommunityCard("forwardsSet", 26, "3rd transport"),# dynamically add name
    CommunityCard("forwardsSet", 16, "move foreard to Go! Collect 200"),#dyna,icall go to 2nd transprt
    CommunityCard("forwardsSet", 12, "move foreward t Go! Collect 200"),# dynamically add name
    #move back
    CommunityCard("move", -3, "move foreward to Go! Collect 200"), 
    #jail
    CommunityCard("getOut", 1, "Get out of jail free card! This can be saved for later."),
    CommunityCard("jail", 1, "Go to jail, Or pay £50 to get out")
])
CommunityCards.cardShuffell()
ChanceCards.cardShuffell()
CardDeck = [#ordered deck where each card corrisponds to the board
"Go",
ShitCreak,
CommunityCards.randomCard(),
APaddle,
CommunityCard("payOut", 200, "Income Tax, £200 has been taken from your account"),
ChungusExpress,
SmokingAlley,
ChanceCards.randomCard(),
TheGreenRoom,
Wellington,
"Jail",
MawhinneyGardens,
DiscordNitro,
LiquorStreet,
BrewDogBoulevard,
PogAir,
JessicasStudio,
CommunityCards.randomCard(),
Ellies,
RakibsHouse,
"Free Parking",
TheCanteena,
ChanceCards.randomCard(),
HothHotel,
TheRazorCrest,
EuropaBus,
Medows,
BelvoirForrest,
SpotifyPremium,
Botanic,
CommunityCard("jail", 0, "Jail\nGo to Jail, Do not pass Go, do not collect £200"),
TheParlour,
ThompsonsGrarage,
CommunityCards.randomCard(),
TheLongfellow,
BigDipper,
ChanceCards.randomCard(),
HotRocks,
CommunityCard("payOut", 100, "Super Tax, £200 has been taken from your account"),
BoulderWorld
]

#===========board state stuff=============
class Board:
    def __init__(self, server):
        self.server = server
        self.playerList = []
       
        self.Deck = CardDeck
        self.propertyCardsKeyed = PropertyCardDeck
        self.propertyCards = [PropertyCardDeck[x] for x in PropertyCardDeck]
        self.chanceCards = ChanceCards
        self.communityChests = CommunityCards
        self.status = None
        self.currentPlayer = None
        self.jail = []
        self.i = 0
        self.boardPicture = None
        self.hiddenBoardMessage = None
        self.BoardPixelLocation = [
            (4400,4400),
            (4000,4600),
            (3600,4600),
            (3200,4600),
            (2800,4600),
            (2400,4600),
            (2000,4600),
            (1600,4600),
            (1200,4600),
            (800,4600),
            (200,4600),# jail
            (0,4000),
            (0,3600),
            (0,3200),
            (0,2800),
            (0,2400),
            (0,2000),
            (0,1600),
            (0,1200),
            (0,800),
            (0,200),#freeparking
            (800,0),
            (1200,0),
            (1600,0),
            (2000,0),
            (2400,0),
            (2800,0),
            (3200,0),
            (3600,0),
            (4000,0),
            (4400,0),#go to jail
            (4400,800),
            (4400,1200),
            (4400,1600),
            (4400,2000),
            (4400,2400),
            (4400,2800),
            (4400,3200),
            (4400,3600),
            (4400,4000)


        ]
    def addPlayer(self, player):
        self.playerList.append(player)
        self.players = cycle(self.playerList)
    def next(self):
        self.i += 1
        if self.i > len(self.playerList)-1:
            self.i = 0
        self.currentPlayer = self.playerList[self.i]
        self.turn(self.currentPlayer)
    def changeStatus(self):
        #do code later
        client.dispatch("speak", self.playerList[0].private, "message")
    def getPlaceName(self, index):
        tmplist = []
        for i in self.Deck:
            if isinstance(i, PropertyCard)or isinstance(i, TransportCard) or isinstance(i, UtilityCard):
                tmplist.append(i.name)
            elif isinstance(i, CommunityCard):
                if i.name == "Super Tax, £200 has been taken from your account":
                    tmplist.append("Super Tax: £100")
                elif i.name == "Income Tax, £200 has been taken from your account":
                    tmplist.append("Income Tax: £200")
                elif i.name == "Jail\nGo to Jail, Do not pass Go, do not collect £200":
                    tmplist.append("Go to Jail")
                elif i in ChanceCards.cards:
                    tmplist.append("Chance Card")
                elif i in CommunityCards.cards:
                    tmplist.append("Community Chest")
                else:
                    tmplist.append("not chance community or tax")
            elif i == "Go":
                tmplist.append(i)
            elif i == "Jail":
                tmplist.append(i)
            elif i == "Free Parking":
                tmplist.append(i)
        return tmplist[index]
    def listAvailableProperty(self):
        tmplist = ["```diff",
                    "=====Property List=====",
                    "\n".join([(("-" if self.propertyCardsKeyed[x].owner != "NotYetAssigned" else "")+str(x)+" - "+self.propertyCardsKeyed[x].colour+": "+self.propertyCardsKeyed[x].name) for x in self.propertyCardsKeyed]),
                    "```"]
        return "\n".join(tmplist)
    def listBoard(self):#lists all of the board positions
        tmplist = []
        for i in self.Deck:
            if isinstance(i, PropertyCard)or isinstance(i, TransportCard) or isinstance(i, UtilityCard):
                tmplist.append(str(self.Deck.index(i))+". "+i.name)
            elif isinstance(i, CommunityCard):
                if i.name == "Super Tax, £200 has been taken from your account":
                    tmplist.append(str(self.Deck.index(i))+". "+"Super Tax: £100")
                elif i.name == "Income Tax, £200 has been taken from your account":
                    tmplist.append(str(self.Deck.index(i))+". "+"Income Tax: £200")
                elif i.name == "Jail\nGo to Jail, Do not pass Go, do not collect £200":
                    tmplist.append(str(self.Deck.index(i))+". "+"Go to Jail")
                elif i in ChanceCards.cards:
                    tmplist.append(str(self.Deck.index(i))+". "+"Chance Card")
                elif i in CommunityCards.cards:
                    tmplist.append(str(self.Deck.index(i))+". "+"Community Chest")
                else:
                    tmplist.append("not chance community or tax")
            elif i == "Go":
                tmplist.append(str(self.Deck.index(i))+". "+i)
            elif i == "Jail":
                tmplist.append(str(self.Deck.index(i))+". "+i)
            elif i == "Free Parking":
                tmplist.append(str(self.Deck.index(i))+". "+i)
        sumUp = ["```\n",
                "=====The monopoly Board=====",
                "\n".join(tmplist),#All boards listed
                "```"]
        return "\n".join(sumUp)
    def sumProperty(self):
        tmplist = ["=====Properties=====",
        ]
    def sendToJail(self, player):
        self.jail.append(player)
    def getOutOfJail(self,player):
        self.jail.remove(player)
        player.getsOutOfJail()
    def turn(self, player):
        if player in self.jail:
            speak(player.general, f"<@{player.member.id}> Its your go but you are in **Jain**. Next go!\nYou have {3-player.turnsSpentInJail} Left. You could also pay £50 to get out or use a get out of jail free card")
            player.turnsSpentInJail += 1
            if player.turnsSpentInJail == 3:
                self.getOutOfJail(player)
        else:
            speak(player.general, f"<@{player.member.id}> Its your go. Roll the die or pass. Nows your chance to buy sell and bargin.")
    def updateBoardImagePlayerPlace(self, player):
        newBoard = Image.open("monopolyBoard.png")
        for i in self.playerList:
            symbol = i.symbol
            coords = self.BoardPixelLocation[i.place]
            newBoard.paste(symbol, coords, symbol.convert('RGBA'))
        newBoard.save("newBoard.png", "png")
        updateBoardPicture(self, "newBoard.png")
    def updateBoardImageHouses(self, property):
        #add transport and utility icons
        if property.houses == 0:
            house = Image.open("Site.png")
        elif property.houses == 1:
            house = Image.open("1Houses.png")
        elif property.houses == 2:
            house = Image.open("2Houses.png")
        elif property.houses == 3:
            house = Image.open("3Houses.png")
        elif property.houses == 4:
            house = Image.open("4Houses.png")
        elif property.houses == 5:
            house = Image.open("Hotel.png")
        else:
            print("house not found")
            house = None
        newBoard = Image.open("monopolyBoard.png")
        coords = self.BoardPixelLocation[self.Deck.index(property)]
        newBoard.paste(house, coords, house.convert('RGBA'))
        newBoard.save("monopolyBoard.png", "png")
        updateBoardPicture(self, "monopolyBoard.png")
    #def bankcrupcy(self, player):
        
#overview   
class SmartView:
    def __init__(self, player):
        self.screen = None
        self.player = player

    def BoardState(self):
        discord.Embed=(

        )
#=======testing==========


#================================================discord stuff==========================================

client = commands.Bot(command_prefix='.')# the command charector for this bot
#non async comands


#===speak
@client.event
async def on_speak(channel, message):
    await channel.send(message)# sends a  amessage into a channel
#the command to activate it
def speak(channel, message):
    client.dispatch("speak", channel, message)


#===satatus update
@client.event
async def on_statusChange(player):
    status  = discord.Embed(
        title = "====================Status Overview====================",
        description = "Hello",
        colour = discord.Colour.blue()
    )
    status.add_field(name = "Your Summery", value = player.sumUp(), inline = False)
    status.set_image(url = player.board.boardPicture.attachments[0].url)
    status.add_field(name ="Other Players Positions",value = "\n".join(["","\n".join([(f"{x.name}: {x.place}") for x in player.board.playerList]),""]),inline=False)
    await player.private.send(embed=status)
#the command to activate it
def statusUpdate(player):
    client.dispatch("statusChange", player)


games =[]
servers = []


#user commands
#on ready
@client.event
async def on_ready():
    print("reporting for duty")
#===start===
@client.command()
async def setup(ctx):# creates or cleans the channels needed for the game, aswell as creates the board object for the server
    #defining varialble 
    server = ctx.guild
    games.append(Board(server))
    board = getBoard(ctx)
    serverCategorys = [x.name for x in server.categories]# getting all of the servers categorys
    #creatting and cleaning the text channels
    if "MONOPOLY" not in serverCategorys: # if there isnt the monopoly category in the server it creates it
        await server.create_category("MONOPOLY")# creates the category
        category = discord.utils.get(server.categories, name = "MONOPOLY")# finds it
        await category.create_text_channel("general-monopoly")# creates the monopoly general
    else:# if its already there
        category = discord.utils.get(server.categories, name = "MONOPOLY")# finds the category
        for channel in category.channels:
            await channel.delete()
        await category.create_text_channel("general-monopoly")
    #setting permisions for general so only players that have joined can see it
    general  = discord.utils.get(category.channels, name = "general-monopoly")#finds the channel
    await general.set_permissions(server.default_role, view_channel = False)#default invisbale
    if discord.utils.get(server.roles, name="Monopoly_Player :)") == None:
        await server.create_role(name = "Monopoly_Player :)")
    role = discord.utils.get(server.roles, name="Monopoly_Player :)")
    await general.set_permissions(role, view_channel = True)
    print("Game Started by",ctx.author.display_name)
    #this creates a hiden channel to put the board in so i can use a http link in the embed
    if discord.utils.get(server.channels, name = "board-hidden") == None: #if its not there it will make it
        boardHiddenChannel = await server.create_text_channel("board-hidden")
        await boardHiddenChannel.set_permissions(server.default_role, view_channel = False)
    else:#deletes it and recreates it if its there
        boardHiddenChannel = discord.utils.get(server.channels, name = "board-hidden")
        await boardHiddenChannel.delete()
        boardHiddenChannel = await server.create_text_channel("board-hidden")
        await boardHiddenChannel.set_permissions(server.default_role, view_channel = False)
    freshBoard = Image.open("hd_assets\\monopolyBoard.png")
    freshBoard.save("monopolyBoard.png", "png")
    updateBoardPicture(board,"monopolyBoard.png")
    print(board.boardPicture.attachments[0].url)

#BoardPicture update
@client.event
async def on_updateBoardPicture(board, path):    
    boardHiddenChannel = discord.utils.get(board.server.channels, name = "board-hidden")
    boardPicture = await boardHiddenChannel.send(file = discord.File(fp=f"C:\\Users\\epicf\\Desktop\\Projects\\MonpolyBot\\{path}"))
    board.boardPicture = boardPicture
    print("hello")

def updateBoardPicture(board, path):
    client.dispatch("updateBoardPicture", board, path)
#===join===
@client.command()
async def join(ctx, symbol = None):
    # settign up needed variables
    server = ctx.guild
    member = ctx.author
    userName = member.display_name
    board = getBoard(ctx)
    privateChannelName = f"{userName} Money".replace(" ", "-").lower()
    category = discord.utils.get(server.categories, name = "MONOPOLY")
    general = discord.utils.get(category.channels, name="general-monopoly")
    privateChannel = discord.utils.get(category.channels, name=privateChannelName)
    #creating players private channel if it doesnt exist, cleaning it if it does exist
    if privateChannel == None: #creates it
        await category.create_text_channel(name = privateChannelName)
        privateChannel = discord.utils.get(category.channels, name=privateChannelName)
    else:#replaces it
        await privateChannel.delete()
        await category.create_text_channel(name = privateChannelName)
        privateChannel = discord.utils.get(category.channels, name=privateChannelName)
    #setting permisions
    await privateChannel.set_permissions(server.default_role, view_channel = False)#default invisable
    await privateChannel.set_permissions(member, view_channel = True)# makes it visable to the player
    if discord.utils.get(server.roles, name="Monopoly_Player :)") not in member.roles:
        await member.add_roles(discord.utils.get(server.roles, name = "Monopoly_Player :)"))
    #creating the player object
    if symbol == None:
        speak(ctx.channel, f"<@{member.id}> You need to pick a symbol, please do .join 'symbol here'\nSymbols can be: !,@,#,&,?,%")
    else:
        if symbol == "!":
            symbol = Image.open("!.png")
        elif symbol == "?":
            symbol = Image.open("q.png")
        elif symbol == "&":
            symbol = Image.open("&.png")
        elif symbol == "#":
            symbol = Image.open("#.png")
        elif symbol == "@":
            symbol = Image.open("@.png")
        elif symbol == "%":
            symbol = Image.open("%.png")
        else:
            speak(general, f"<@{member.id}> You need to pick a symbol, please do .join 'symbol here'\nSymbols can be: !,@,#,&,?,%")
        player = Player(userName, 1500, member, privateChannel, category, general, board, symbol)
        board.addPlayer(player)
        await player.private.send(board.listBoard())
        print(userName, "has joined the game")

#===roll===
@client.command()
async def roll(ctx):
    #defining variables
    board = getBoard(ctx)
    player = getPlayer(ctx, board)
    player.roll()
    print(player.lastRoll)
    if player.inJail == False:
        player.moveForward(player.lastRoll)
        board.updateBoardImagePlayerPlace(player)
        print(f"player landed on {board.getPlaceName(player.place)}")#

#===buying===
@client.command()
async def buy(ctx, propertyNumber):
    #defining variables
    board = getBoard(ctx)
    player = getPlayer(ctx, board)
    #getting the proeprty
    theProperty = board.Deck[int(propertyNumber)]
    if theProperty in board.propertyCards:# if its a property you can buy that isnt owned
        if theProperty.owner == player:# if the property is owned by the player
            theProperty.buyHouse()
        else:
            player.buyProperty(theProperty)
    else:
        await player.private.send("You cannot buy this")

#===give===
@client.command()
async def give(ctx, value, target="default"):
    board = getBoard(ctx)
    player = getPlayerFromName(ctx.message.mentions[0].display_name, board)
    player.payIn(int(value))

#===take===
@client.command()
async def take(ctx, value, target="default"):
    board = getBoard(ctx)
    player = getPlayerFromName(ctx.message.mentions[0].display_name, board)
    player.payBank(int(value))

#===status===
@client.command()
async def status(ctx):
    board = getBoard(ctx)
    player = getPlayer(ctx,board)
    statusUpdate(player)

#===sell===
@client.command()
async def sell(ctx, item, value = None, target = None):
    board = getBoard(ctx)
    player = getPlayer(ctx, board)
    theProperty = board.Deck[int(item)]
    if target == None and value == None:# if its just the number of the property it means sell house
        if theProperty == board.propertyCardsKeyed[int(item)]:# if its on the board
            theProperty.sellHouse()      
        else:
            speak(player.general, "you cannot sell that")
        return None
    elif "@" in target and theProperty == board.propertyCardsKeyed[int(item)]:
        target = getPlayerFromName(ctx.message.mentions[0].display_name, board)
        theProperty.transferOwner(target)
        target.payPlayer(player, int(value))
        await player.general.send(f"**{player.name}** sold **{theProperty.name}** to {target.name}")
    else:
        speak(player.general, "you cannot sell that") 
    
#===pay===
@client.command()
async def pay(ctx, value = "default", target = None):
    board = getBoard(ctx)
    player = getPlayer(ctx, board)
    if value == "default" and board.Deck[player.place] in board.propertyCards and board.Deck[player.place] != "NotYetAssigned":# if paying to location and location is a property that can pay rent
        theProperty = board.Deck[player.place]
        player.payRent(theProperty)
    elif value == "default" and (player.place == 4 or player.place == 38):#must be a tax, this is handeled witha community card
        card = board.Deck[player.place]
        card.activate(player)
    elif value == "jail":
        if player.inJail and target == None:
            player.payBank(50)
            board.getOutOfJail(player)
            speak(player.general, f"<@{player.member.id}> Got **out of jail**. They're now back in the game")
        elif player.inJail and target == "card":
            if player.getOutOfJailFree > 0:
                player.getOutOfJailFree -= 1
                board.getOutOfJail(player)
                speak(player.general, f"<@{player.member.id}> Got **out of jail**. They're now back in the game")
            else:
                speak(player.general, "You dont have any get out of jail free cards")  
        else:
            speak(player.general, "You are not in jail")
        
    if target != None and value != "default" and value != "jail": 
        target = getPlayerFromName(ctx.message.mentions[0].display_name, board)
        player.payPlayer(target, value)

#===move===
@client.command()
async def move(ctx, position):
    board = getBoard(ctx)
    player = getPlayer(ctx, board)
    if int(position)>=0 and int(position)<=39:
        player.place = int(position)
        player.moveForward(0)
    else:
        speak(player.general,f"**{position}** is not a valid position, between 0 and 39")

##==community chests===
@client.command()
async def community(ctx):
    board = getBoard(ctx)
    player = getPlayer(ctx, board)
    card = CommunityCards.randomCard()
    card.activate(player)
    speak(player.general, f"<@{player.member.id}> picked up Community Card:\n{card.name}")

#===Chance cards===
@client.command()
async def chance(ctx):
    board = getBoard(ctx)
    player = getPlayer(ctx, board)
    card = ChanceCards.randomCard()
    card.activate(player)
    speak(player.general, f"<@{player.member.id}> picked up Chance Card:\n{card.name}")

@client.command()
async def deeds(ctx, propertyNumber):
    board = getBoard(ctx)
    player = getPlayer(ctx, board)
    propertyNumber = int(propertyNumber)
    if propertyNumber in [x for x in board.propertyCardsKeyed]:#checks if the property number is a property
        theProperty = board.propertyCardsKeyed[propertyNumber]
        await player.private.send(theProperty.sumUp())
    else:
        await player.private.send("That is not a valad property.")

#===list===
@client.command()
async def list(ctx, stuff = "default"):
    board = getBoard(ctx)
    player = getPlayer(ctx, board)
    if stuff == "default":
        await ctx.channel.send(board.listAvailableProperty())
#===start===
@client.command()
async def start(ctx):
    board = getBoard(ctx)
    board.next()

#===next===
@client.command()
async def next(ctx):
    board = getBoard(ctx)
    board.next()

#===go to jail===
@client.command()
async def jail(ctx, target = None):
    board = getBoard(ctx)
    player = getPlayer(ctx, board)
    if target == None:
        player.goesToJail()
    else:
        target = getPlayerFromName(ctx.message.mentions[0].display_name, board)
        target.goesToJail()

#===jail card===
@client.command()
async def jailcard(ctx, target = None):
    board = getBoard(ctx)
    player = getPlayer(ctx, board)
    if target == None:
        player.getOutOfJailFree +=1
    else:
        target = getPlayerFromName(ctx.message.mentions[0].display_name, board)
        target.getOutOfJailFree +=1#

#===mortage===
@client.command()
async def mortgage(ctx, propertyNumber):
    board = getBoard(ctx)
    player = getPlayer(ctx, board)
    theProperty = board.Deck[int(propertyNumber)]
    if theProperty in board.propertyCards:
        theProperty.mortgage()

#===demortage===
@client.command()
async def demortgage(ctx, propertyNumber):
    board = getBoard(ctx)
    player = getPlayer(ctx, board)
    theProperty = board.Deck[int(propertyNumber)]
    if theProperty in board.propertyCards:
        theProperty.deMortgage()

#===clear===
@client.command()
async def clear(ctx, amount = 1):
    await ctx.channel.purge(limit=amount)


Token = open("hidden/BotToken.json","r")
Token = json.loads(Token.read())
client.run(Token)
