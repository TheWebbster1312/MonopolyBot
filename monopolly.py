#=======================imports===============================
import random
import discord
import json
from discord.abc import PrivateChannel
#import request
from discord.appinfo import AppInfo
from discord.ext import commands, tasks
from itertools import cycle
#=======================derfining variables and global Meathods===================
playerList = []
jail = []
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
def getPlayerFromName(display_name):
    for i in playerList:
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
        self.morgate = self.siteValue/2
        self.owner = "NotYetAssigned"
        self.houses = 0
        self.rent = self.rentList[self.houses]
        self.monopolized = False

    def assignOwner(self,newOwner):#sets the owner of the property, when they buy the property
        self.owner = newOwner
        self.owner.update(self)
        self.owner.payBank(self.siteValue)
    def transferOwner(self,newOwner):#sets the new owenr for free
        self.owner.removeProperty(self)
        self.owner = newOwner
        self.owner.update(self)
        self.houses = 0
    def updateRent(self): #will update the rent value based on houses owned
        self.rent = self.rentList[self.houses]
    def buyHouse(self):#adds a house === and error catching for unassigned owner and only upgrade them linearly
        if self.houses < 5:
            if self.monopolized:
                if self.checkNeighbourEquivilent():
                    self.houses += 1
                    self.owner.payBank(self.costOfHouse)
                    self.updateRent()
                else:
                    print("you must have all properties at the same number of house before you buy more")
            else:
                print("You need to monopolize "+self.colour+" to buy a house first")
        else:
            print("too many houses")
    def subHouse(self):#takes away a house
        self.house += -1
    def monopolize(self):
        self.monopolized = True
        if self.houses == 0:
            self.rent = self.rent*2
    def deMonopolize(self):
        self.monopolized = False
        if self.houses == 0:
            self.rent = self.rentList[0]
    def checkNeighbourEquivilent(self):
        self.neibouringStreets = []
        for i in self.owner.properties[self.colour]: 
            if isinstance(i,int):# checks if its an intager and skips
                continue
            self.neibouringStreets.append(i.houses)
        for i in self.neibouringStreets:
            if self.neibouringStreets[0] >= self.houses:
                continue
            else: 
                return False
        return True
    def sumUp(self):
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
                "```"]
        return "\n".join(sumUp)
#=======================transport cards===================
class TransportCard:
    def __init__(self, name):
        self.name = name
        self.siteValue = 200
        self.colour = "transport"
        self.owner = "NotYetAssigned" 
        self.rentList = [25,50,100,200]
        
    def assignOwner(self, newOwner):
        self.owner = newOwner
        self.owner.update(self)
        self.owner.payOut(self.siteValue)
        self.updateRent()
    def transferOwner(self,newOwner):#sets the new owenr for free
        self.owner.removeProperty(self)
        self.owner = newOwner
        self.owner.update(self)
    def updateRent(self):
        self.rent = self.rentList[len(self.owner.properties["transport"])]
        for i in self.owner.properties["transport"]:
            if i != self: i.updateRent()
    def sumUp(self):
        sumUp = [f"```\n=======Deeds for {self.name}=======",
                f"Type: {self.colour}",
                f"Site Value: £{self.siteValue}",
                "===Rent===",
                f"1 Transport owned: £{self.rentList[0]}",
                f"2 Transports owned: £{self.rentList[1]}",
                f"3 Transports owned: £{self.rentList[2]}",
                f"4 Transports owned: £{self.rentList[3]}",
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
        self.owner = newOwner
        self.owner.update(self)
    def updateRent(self, roll):
        if len(self.owner.properties["utility"]) < 2:
            self.rent = 4*roll
        else:
            self.rent = 10*roll
    def sumUp(self):
        sumUp = [f"```\n=======Deeds for {self.name}=======",
                f"Type: {self.colour}",
                f"Site Value: £{self.siteValue}",
                "===Rent===",
                f"1 Utility owned: 4 x Players roll",
                f"2 Utility owned: 10 x Players roll",
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
            player.moveBackwards(player.place-self.value)
        elif self.Type == "move":
            if self.value > 0: 
                player.moveForward(self.value)
            else: 
                player.moveBackwards(self.value) 
        elif self.Type == "getOut": 
            player.getOutOfJail += 1
        elif self.Type == "jail": 
            player.goesToJail
        else: 
            print("error, please select valid card", self.Type)
        self.customFunc()
#=======================player class=======================
class Player:
    def __init__(self, name, cash, member = None, private = None, category = None, general = None):
        self.name = name
        self.cash = cash
        self.inJail = False
        self.getOutOfJail = 0
        self.place = 0
        self.lastRoll = 0
        self.rollValue = [0,0]
        self.private = private
        self.category = category
        self.general = general
        self.member = member

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
    def roll(self):
        self.rollValue = [random.randint(1,6), random.randint(1,6)]
        self.lastRoll = self.rollValue[0]+self.rollValue[1]
    def payOut(self, amount):#the player pays the amount
        self.cash = self.cash-amount
    def payIn(self, amount):#the player gets the amount
        self.cash = self.cash+amount
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
        property.assignOwner(self)
    def payRent(self, property):
        if property.colour == "utility": property.updateRent(self.lastRoll)# calculates rent based on roll
        if property.rent > self.cash:
            self.payPlayer(property.owner, self.cash)
            bankrupcy(self, property.owner)
        else:
            self.payPlayer(property.owner, property.rent)
    def payBank(self,value):
        if value > self.cash:
            self.payOut(self.cash)
            bankrupcy(self, "bank")
        else:
            self.payOut(value)
    def payPlayer(self,player,value):
        self.cash -= value
        player.cash +=value
    def goesToJail(self):
        if self.getOutOfJail > 0:
            print("you got out of jail free using your card")
            self.getOutOfJail += -1
            jail.append(self)
        else:
            self.place = 11
    def getsOutOfJail(self):
        self.cash = self.cash -50
        jail.remove(self)
    def moveForward(self, value):
        self.place += value
        if self.place > 39:
            self.place = self.place - 39
            self.payIn(200)
    def moveBackwards(self, value):
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
    def getPropertyNamesEmoji(self):
        self.PropertyNamesEmoji = []
        for i in self.getProperties():
            houses = ":house: "
            addon = ""
            prefix = "```"
            if isinstance(i, PropertyCard):
                for _ in range(1,i.houses):
                    addon = addon+houses
                if i.houses == 5:
                    addon = ":hotel:"
                #prefix
                if i.colour == "pink" or i.colour == "red":
                    prefix = "```diff\n-"
                elif i.colour == "darkBlue":
                    prefix = "```md\n"
                elif i.colour == "lightBlue":
                    prefix =  "```yaml\n"
                elif i.colour == "green":
                    prefix = "```css\n"
                elif i.colour == "yellow":
                    prefix = "```fix\n"
                elif i.colour == "orange" or i.colour == "brown":
                    prefix = "```glsl\n"
                else:
                    prefix = "```"
            self.PropertyNamesEmoji.append(prefix+i.name+" "+addon+"\n```")
        return self.PropertyNamesEmoji
    def sumUp(self):
        sumUp = [f"```\n=======Overview {self.name}=======",
                f"Cash: £{self.cash}",
                f"Current Position: {self.place}",
                "===Properties===",
                "\n".join(["    -"+x.colour +": "+x.name+"; Houses: "+str(x.houses if isinstance(x,PropertyCard) else "")+(str("; Rent: "+str(x.rent)) if isinstance(x,PropertyCard) else "") for x in self.getProperties()]),
                "===Monopolys===",
                "\n".join(["    -"+x for x in self.monopolys]),
                "===Jail Status===",
                f"In Jail: {self.inJail}",
                f"Get put of Jail free cards: {self.getOutOfJail}"
                "```"]
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
CommunityCard("payOut", 100, "Income Tax, £200 has been taken from your account"),
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
"Free parking",
TheCanteena,
ChanceCards.randomCard(),
HothHotel,
TheRazorCrest,
EuropaBus,
Medows,
BelvoirForrest,
SpotifyPremium,
Botanic,
CommunityCard("jail", 0, "Go to Jail, Do not pass Go, do not collect £200"),
TheParlour,
ThompsonsGrarage,
CommunityCards,
TheLongfellow,
BigDipper,
ChanceCards,
HotRocks,
CommunityCard("payOut", 100, "Super Tax, £200 has been taken from your account"),
BoulderWorld
]

#===========board state stuff=============
class Board:
    def __init__(self, server):
        self.server = server
        self.playerList = []
        self.players = []
        self.Deck = CardDeck
        self.PropertyCards = PropertyCardDeck
        self.ChanceCards = ChanceCards
        self.CommunityChests = CommunityCards
        self.status = None
        self.turn = None
    def addPlayer(self, player):
        self.playerList.append(player)
        self.players = cycle(self.playerList)
    def next(self):
        self.turn = next(self.players)
        print(self.turn)
    def changeStatus(self):
        #do code later
        return None
    def getPlaceName(self, index):
        tmplist = []
        for i in self.Deck:
            if isinstance(i, PropertyCard or TransportCard or UtilityCard):
                tmplist.append(i.name)
            elif isinstance(i, CommunityCard):
                if i.name == "Super Tax, £200 has been taken from your account":
                    tmplist.append("Super Tax: £100")
                elif i.name == "Income Tax, £200 has been taken from your account":
                    tmplist.append("Income Tax: £200")
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
    def listBoard(self):#lists all of the board positions
        tmplist = []
        for i in self.Deck:
            if isinstance(i, PropertyCard or TransportCard or UtilityCard):
                tmplist.append(str(self.Deck.index(i))+". "+i.name)
            elif isinstance(i, CommunityCard):
                if i.name == "Super Tax, £200 has been taken from your account":
                    tmplist.append(str(self.Deck.index(i))+". "+"Super Tax: £100")
                elif i.name == "Income Tax, £200 has been taken from your account":
                    tmplist.append(str(self.Deck.index(i))+". "+"Income Tax: £200")
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
        

#=======testing==========


#================================================discord stuff==========================================

client = commands.Bot(command_prefix='.')# the command charector for this bot
#client comands


games =[]
servers = []
#user commands
#on ready
@client.event
async def on_ready():
    print("reporting for duty")
#===start===
@client.command()
async def start_game(ctx):# creates or cleans the channels needed for the game, aswell as creates the board object for the server
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
    await server.create_role(name = "Monopoly_Player")
    role = discord.utils.get(server.roles, name="Monopoly_Player")
    await general.set_permissions(role, view_channel = True)
    print("Game Started by",ctx.author.display_name)
#===join===
@client.command()
async def join(ctx):
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
        await PrivateChannel.delete()
        await category.create_text_channel(name = privateChannelName)
        privateChannel = discord.utils.get(category.channels, name=privateChannelName)
    #setting permisions
    await privateChannel.set_permissions(server.default_role, view_channel = False)#default invisable
    await privateChannel.set_permissions(member, view_channel = True)# makes it visable to the player
    await member.add_roles(discord.utils.get(server.roles, name = "Monopoly_Player"))
    #creating the player object    
    player = Player(userName, 1500, member, privateChannel, category, general)
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
    player.moveForward(player.lastRoll)
    print(f"player landed on {board.getPlaceName(player.place)}")


Token = open("hidden/BotToken.json","r")
Token = json.loads(Token.read())
client.run(Token)
