import os, sys
import random
import math
import pygame
from pygame.locals import *
from tetromino import *

'''
FUNCTIONALITY YET TO ADD:
- Better turning mechanics (near walls, etc.)
- Timer, line counter for time-to-40
- Start screen, instructions, options (speed thresholds, etc.)
- Different game modes
- Add text for next piece, stored piece, score, (highscore) (add boxes for next piece/stored piece)
- Add color to placed blocks (? Not sure if I even want this)
'''

class Tetris:
	colors = {'RED':pygame.Color(255,0,0),
	          'PURPLE':pygame.Color(128,0,128),
			  'GREEN':pygame.Color(0,128,0),
			  'AQUA':pygame.Color(0,255,255),
			  'BLUE':pygame.Color(0,0,255),
			  'ORANGE':pygame.Color(128,0,0),
			  'YELLOW':pygame.Color(255,255,0),
			  'PINK':pygame.Color(255,51,153),
			  'SEA':pygame.Color(0,102,102),
			  'GRAY':pygame.Color(100,100,100),
			  'BLACK':pygame.Color(0,0,0),
			  'WHITE':pygame.Color(255,255,255)}
	
	# Shapes of tetrominos
	genres = ['LONG','RHOOK','LHOOK','SQUARE','SBLOCK',
			  'TBLOCK','ZBLOCK']
	
	FPS = 120
	fpsClock = pygame.time.Clock()
	
	# the unit size of a block (for the grid and tetromino blocks)
	blockSize = 40
	
	# width of sidebars
	barWidth = int(blockSize*2.5)
	# dimensions of play area in blockSize units
	widthInBlocks = 12
	heightInBlocks = 20
	
	'''
	Initiate game.
	Width can be specified, but mostly should just be changed in the above variables.
	Ditto height.
	'''
	def __init__(self, width=blockSize*widthInBlocks+barWidth*2, height=blockSize*heightInBlocks):
		pygame.init()
		self.width = width # width with sidebars
		self.gameWidth = self.width - self.barWidth*2 # width w/out sidebars
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))
		
		self.score = 0
		self.highScore = 0
		
		# the next block to fall. Will be set in newBlock() method
		self.nextBlock = None
		
		# stored block, and a boolean for whether we switched this block already
		self.storedBlock = None
		self.switchedThisBlock = False
		
		# draw the sidebars/walls
		self.walls = [pygame.Rect(0,0,self.barWidth,self.height),pygame.Rect(self.width-self.barWidth,0,self.barWidth,self.height)]
		
		# array of placed blocks (from fallen tetrominos)
		# it has gameWidth/blockSize columns and height/blockSize rows
		self.placedBlocks = [[None for x in range(int(self.gameWidth/self.blockSize))] for y in range(int(self.height/self.blockSize))]
		
		# set the location where new tetrominos will spawn
		self.startCoordinates = (self.barWidth + self.blockSize*2,0)
		
		pygame.display.set_caption('Tetris!')
	
	# Reset all aspects of the game (except high score)
	def restart(self):
		self.score = 0
		self.nextBlock = None
		self.placedBlocks = [[None for x in range(int(self.gameWidth/self.blockSize))] for y in range(int(self.height/self.blockSize))]
		self.storedBlock = None
		self.switchedThisBlock = False
		self.newBlock()
	
	# Spawn a new block, as well as a random next block.
	# (In most cases the new block is just the previous next block, so there's only one random choice.)
	def newBlock(self):
		self.switchedThisBlock = False
		genre = random.choice(self.genres)
		
		# There is no next block on new game or reset, so we spawn a random one.
		if self.nextBlock == None:
			self.tetro = Tetromino(genre,self.blockSize,
						  self.startCoordinates[0],self.startCoordinates[1], self.height, self.placedBlocks)
		else:
			self.tetro = Tetromino(self.nextBlock.genre,self.blockSize,
								   self.startCoordinates[0],self.startCoordinates[1], self.height, self.placedBlocks)
		
		# Shows the next block on the right sidebar
		self.nextBlock = Tetromino(genre,int(self.barWidth/5),self.width-(4*int(self.barWidth/5)),int(self.height/4), self.height, self.placedBlocks)
		
	# draw everything onto the screen
	def drawScreen(self):
		# draw background and walls
		self.screen.fill(self.colors['BLACK'])
		for w in self.walls:
			pygame.draw.rect(self.screen,self.colors['GRAY'],w)
		
		# display score-text and score
		myFont = pygame.font.SysFont("monospace", 15)
		scoreString = myFont.render(str(self.score), 1, self.colors['WHITE'])
		scoreText = myFont.render("Score:",1,self.colors['WHITE'])
		scoreDimensions = myFont.size(str(self.score))
		scoreTextDimensions = myFont.size("Score:")
		self.screen.blit(scoreText, (self.width-self.barWidth+1,0))
		self.screen.blit(scoreString, (self.width-scoreDimensions[0],scoreTextDimensions[1]))
		
		# display high-score text and high-score
		highScoreString = myFont.render(str(self.highScore),1,self.colors['WHITE'])
		highScoreText = myFont.render("High Score:",1,self.colors['WHITE'])
		highScoreDimensions = myFont.size(str(self.highScore))
		highScoreTextDimensions = myFont.size("High Score:")
		self.screen.blit(highScoreText, (self.width-self.barWidth+1, highScoreTextDimensions[1]*3))
		self.screen.blit(highScoreString, (self.width-highScoreDimensions[0], highScoreTextDimensions[1]*4))
		
		# draw the placed blocks
		for row in self.placedBlocks:
			for b in row:
				if b != None:
					pygame.draw.rect(self.screen,self.colors["RED"],b)
		
		# draw the current tetromino
		for b in self.tetro.rectGroup:
			pygame.draw.rect(self.screen,self.colors[self.tetro.blockColor],b)
		
		# if relevant, draw the current tetromino's ghost at the bottom of the screen
		# and draw the next block
		if self.tetro.alive:
			for b in self.tetro.ghostBlocks:
				pygame.draw.rect(self.screen,self.colors['WHITE'],b)
			for b in self.nextBlock.rectGroup:
				pygame.draw.rect(self.screen,self.colors[self.nextBlock.blockColor],b)
		
		# draw the stored block
		if self.storedBlock != None:
			for b in self.storedBlock.rectGroup:
				pygame.draw.rect(self.screen,self.colors[self.storedBlock.blockColor],b)
		
		# draw gridlines
		for y in range(self.blockSize,self.height,self.blockSize):
			pygame.draw.line(self.screen,self.colors['WHITE'],(self.barWidth,y),(self.width-self.barWidth,y))
		for x in range(self.barWidth+self.blockSize,self.width-self.barWidth,self.blockSize):
			pygame.draw.line(self.screen,self.colors['WHITE'],(x,0),(x,self.height))
				
	# Clear rows when they're full of tetrominos
	def clearRows(self):
		emptyRows = [] # list of indices of empty rows
		for rowIdx in range(len(self.placedBlocks)):
			if None not in self.placedBlocks[rowIdx]:
				emptyRows.append(rowIdx)
				# empty the row
				self.placedBlocks[rowIdx] = [None for x in range(int(self.gameWidth/self.blockSize))]
		
		# for each empty row,
		# change the y-val of everything above it to move each block down one row
		for row in emptyRows:
			for rowIdx in range(row):
				for i in self.placedBlocks[rowIdx]:
					if i != None:
						i.y+=self.blockSize
		
		# remake the 2D Array, then fill it with our newly-recalibrated placed blocks
		newArray = [[None for x in range(int(self.gameWidth/self.blockSize))] for y in range(int(self.height/self.blockSize))]
		for row in self.placedBlocks:
			for elt in row:
				if elt != None:
					xIdx = int((elt.x-self.barWidth)/self.blockSize)
					yIdx = int(elt.y/self.blockSize)
					newArray[yIdx][xIdx] = elt
		self.placedBlocks = newArray
		
		# Points! Bonuses for multi-line clears.
		clearedRows = len(emptyRows)
		if clearedRows==1:
			self.score += 100
		elif clearedRows==2: # bonus: 1.25x
			self.score += 250
		elif clearedRows==3: # bonus: 1.5x
			self.score += 450
		elif clearedRows==4: # big bonus: 2x
			self.score += 800
		# update highscore if relevant
		self.highScore = max(self.score, self.highScore)
	
	# deal with the death of a tetromino
	def blockDeath(self):		
		# adds block to placedBlocks
		for b in self.tetro.rectGroup:
			xIdx = int((b.x-self.barWidth)/self.blockSize)
			yIdx = int(b.y/self.blockSize)
			self.placedBlocks[yIdx][xIdx] = b
		
		# clear rows if relevant
		self.clearRows()
	
	# pause method. also handles exiting the game
	def pause(self):
		# display a screen with PAUSE and
		# Q TO QUIT and ESC TO UNPAUSE
		pauseScreen = pygame.Surface((self.width, self.height))
		
		pauseScreen.fill(self.colors['BLUE'])
		pauseScreen.set_alpha(128)
		self.screen.blit(pauseScreen, (0,0))
		
		# pausescreen text
		pauseText = "PAUSED"
		'''TOO LONG'''
		instructionText = "F TO STORE, Q TO QUIT, ESC TO UNPAUSE"
		resetText = "R TO RESTART"
		
		myFont = pygame.font.SysFont("monospace", 30, 1)
		pauseWord = myFont.render(pauseText, 1, self.colors['RED'])
		instructions = myFont.render(instructionText,1,self.colors['RED'])
		resetWord = myFont.render(resetText,1,self.colors['RED'])
		
		pauseWordDimensions = myFont.size(pauseText) # duple (width, height)
		instructionsDimensions = myFont.size(instructionText)
		resetDimensions = myFont.size(resetText)
		
		self.screen.blit(pauseWord, ((int(self.width-pauseWordDimensions[0])/2),int(self.height/4)))
		self.screen.blit(instructions, ((int(self.width-instructionsDimensions[0])/2),int(self.height/2)))
		self.screen.blit(resetWord, ((int(self.width-resetDimensions[0])/2),int(3*self.height/4)))
				
		pygame.display.flip()
		
		
		pauseStart = pygame.time.get_ticks()
		while True:
			self.fpsClock.tick(self.FPS)
			
			done = False
			
			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if e.type == pygame.KEYDOWN:
					# press q to quit
					if e.key == pygame.K_q:
						pygame.quit()
						sys.exit()
					if e.key == pygame.K_r:
						self.restart()
						done = True # unpause
				# resume the game
					if e.key == pygame.K_ESCAPE and pygame.time.get_ticks()-pauseStart>200:
						done = True
			if done: break
	
	# returns true if the game is over, false otherwise
	def checkGameOver(self):
		for e in self.tetro.rectGroup:
			for y in self.placedBlocks:
				for x in y:
					if x != None and e.colliderect(x):
						return True
		return False
	
	def endGame(self):
		# display gameOver text and wait for input
				
		self.drawScreen()
		
		gameOverScreen = pygame.Surface((self.width, self.height))
		
		gameOverScreen.fill(self.colors['RED'])
		gameOverScreen.set_alpha(128)
		self.screen.blit(gameOverScreen, (0,0))
		
		# gameOverScreen text
		text1 = "GAME OVER"
		text2 = "FINAL SCORE: " + str(self.score)
		text3 = "Q TO QUIT, R TO RESTART"
		#text3 = "Q TO QUIT"
		
		myFont = pygame.font.SysFont("monospace", 30, 1)
		doneText1 = myFont.render(text1,1,self.colors['BLUE'])
		doneText2 = myFont.render(text2,1,self.colors['BLUE'])
		doneText3 = myFont.render(text3,1,self.colors['BLUE'])

		text1Dimensions = myFont.size(text1) # duple (width, height)
		text2Dimensions = myFont.size(text2)
		text3Dimensions = myFont.size(text3)
		
		self.screen.blit(doneText1, ((int(self.width-text1Dimensions[0])/2),int(self.height/4)))
		self.screen.blit(doneText2, ((int(self.width-text2Dimensions[0])/2),int(self.height/2)))
		self.screen.blit(doneText3, ((int(self.width-text3Dimensions[0])/2),int(3*self.height/4)))
				
		pygame.display.flip()
		
		pauseStart = pygame.time.get_ticks()
		done = False
		while not done:
			self.fpsClock.tick(self.FPS)
			
			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if e.type == pygame.KEYDOWN:
					# press q to quit
					if e.key == pygame.K_q:
						pygame.quit()
						sys.exit()
					# press r to restart
					if e.key == pygame.K_r:
						self.restart()
						done = True
	
	def MainLoop(self):
		self.newBlock()
		lastRotation = pygame.time.get_ticks()
		timeAtLastDrop = pygame.time.get_ticks()
		lastHardDrop = pygame.time.get_ticks()
		timeBetweenRotations = 150
		timeBetweenHardDrops = 250
		timeBetweenMoves = 75
		
		lastLeft = pygame.time.get_ticks()
		lastRight = pygame.time.get_ticks()
		lastDown = pygame.time.get_ticks()
		
		while True:
			self.fpsClock.tick(self.FPS)
			
			for e in pygame.event.get():
				if e.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
					self.pause()

			# gravity
			timeNow = pygame.time.get_ticks()
			# initially drop once per second, increasing in speed with higher score
			if timeNow - timeAtLastDrop > 1000*(math.e**(-1.*self.score/10000)):
				timeAtLastDrop = timeNow
				self.tetro.move(0,self.blockSize,self.walls,self.placedBlocks)
						
			key = pygame.key.get_pressed()
			# LEFT, RIGHT, or DOWN to move the tetromino
			if key[pygame.K_LEFT] and self.tetro.alive:
				tmp = pygame.time.get_ticks()
				if tmp - lastLeft > timeBetweenMoves:
					lastLeft = tmp
					self.tetro.move(-self.blockSize,0,self.walls, self.placedBlocks)
			if key[pygame.K_RIGHT] and self.tetro.alive:
				tmp = pygame.time.get_ticks()
				if tmp - lastRight > timeBetweenMoves:
					lastRight = tmp
					self.tetro.move(self.blockSize,0,self.walls,self.placedBlocks)
			if key[pygame.K_DOWN] and self.tetro.alive:
				tmp = pygame.time.get_ticks()
				if tmp - lastDown > timeBetweenMoves:
					lastDown = tmp
					self.tetro.move(0,self.blockSize,self.walls,self.placedBlocks)
			
			# UP to rotate
			if key[pygame.K_UP]:
				tempTime = pygame.time.get_ticks()
				if tempTime - lastRotation > timeBetweenRotations:
					lastRotation = tempTime
					self.tetro.rotate(self.walls, self.placedBlocks, "CW")
			
			# or F to rotate right and D to rotate left
			if key[pygame.K_d]:
				tempTime = pygame.time.get_ticks()
				if tempTime - lastRotation > timeBetweenRotations:
					lastRotation = tempTime
					self.tetro.rotate(self.walls, self.placedBlocks, "CW")
			if key[pygame.K_s]:
				tempTime = pygame.time.get_ticks()
				if tempTime - lastRotation > timeBetweenRotations:
					lastRotation = tempTime
					self.tetro.rotate(self.walls, self.placedBlocks, "CCW")
			
			# F stores/switches with the stored block
			if key[pygame.K_f]:
				if not self.switchedThisBlock:
					if self.storedBlock == None:
						self.storedBlock = Tetromino(self.tetro.genre,int(self.barWidth/5),
													 int(self.barWidth/5),int(self.height/4),self.height,self.placedBlocks)
						self.newBlock()
					else:
						temp = self.storedBlock
						self.storedBlock = Tetromino(self.tetro.genre,int(self.barWidth/5),
													 int(self.barWidth/5),int(self.height/4),self.height,self.placedBlocks)
						self.tetro = Tetromino(temp.genre,self.blockSize,
											   self.startCoordinates[0],self.startCoordinates[1],
											   self.height, self.placedBlocks)
					
					self.switchedThisBlock = True
			
			# SPACE to harddrop
			if key[pygame.K_SPACE]:
				tempTime = pygame.time.get_ticks()
				if tempTime - lastHardDrop > timeBetweenHardDrops:
					lastHardDrop = tempTime
					while self.tetro.alive:
						self.tetro.move(0,self.blockSize,self.walls,self.placedBlocks)
			
			# deal with a dead tetromino and/or endgame
			if not self.tetro.alive:
				self.blockDeath()
				self.newBlock()
				
				if self.checkGameOver():
					self.endGame()

			self.drawScreen()
			pygame.display.flip()
		

def main():
	os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50,50)
	t = Tetris()
	t.MainLoop()

if __name__=='__main__':
	main()
