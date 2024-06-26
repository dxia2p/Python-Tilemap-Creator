import pygame
import pygame.math
import GuiLib as GuiLib
import sys
import SaveSystem
from tkinter import filedialog
import os

# Grid Constants
GRID_SIZE = 30
GRID_ROW_COUNT = 51
GRID_COLUMN_COUNT = 51

# Font Constant
ROBOTO_REGULAR_PATH = "Roboto/Roboto-Regular.ttf"

class Tile: # class to store information about tile at position in grid
    tilemap = [[None] * GRID_COLUMN_COUNT for i in range(GRID_ROW_COUNT)] # static 2d array 
    def __init__(self, position, tileTemplate): # important to note that position refers to the position in the tilemap's grid (position >= 0, position has to be an integer)

        self.position = position
        self.tileTemplate = tileTemplate
        Tile.tilemap[int(position.x)][int(position.y)] = self
    def drawTile(self):
        Camera.drawTexture(self.tileTemplate.texture, (self.position * GRID_SIZE) - pygame.Vector2(GRID_SIZE / 2, GRID_SIZE / 2), pygame.Vector2(GRID_SIZE, GRID_SIZE))

    @staticmethod
    def addTile(gridPosition, tileTemplate):
        """gridPosition is in tilemap coordinates, has to be >= 0 and an integer"""
        if gridPosition.x >= 0 and gridPosition.x < GRID_COLUMN_COUNT and gridPosition.y >= 0 and gridPosition.y < GRID_ROW_COUNT:
            return Tile(gridPosition, tileTemplate)
        #else:
            #print(f"Tile position at {gridPosition.x}, {gridPosition.y} is out of bounds!")
    
    @staticmethod
    def removeTileAtPos(gridPosition): # removes a tile
        t = Tile.tilemap[int(gridPosition.x)][int(gridPosition.y)]
        if t == None:
            #print(f"Invalid tile, could not remove tile at {gridPosition.x}, {gridPosition.y}")
            return
        Tile.tilemap[int(gridPosition.x)][int(gridPosition.y)] = None
    
    @staticmethod
    def drawAllTiles(): 
        """This must be called every frame to draw all the tiles"""
        for i in range(len(Tile.tilemap)):
            for j in range(len(Tile.tilemap)):
                if Tile.tilemap[i][j] != None:
                    Tile.tilemap[i][j].drawTile()
    
    @staticmethod
    def removeTileByTemplate(template): # remove all tiles using this tile template
        for i in range(len(Tile.tilemap)):
            for j in range(len(Tile.tilemap[i])):
                if Tile.tilemap[i][j] != None and Tile.tilemap[i][j].tileTemplate == template:
                    Tile.removeTileAtPos(pygame.Vector2(i, j))

class TileTemplate: # this is for the "template" of each tile
    selectedTile = None
    tiles = []

    increaseIdButtonTexture = None
    decreaseIdButtonTexture = None
    deleteButtonTexture = None

    maxTileTemplateGUICount = 12
    TemplateGUIStartRange = 0

    def onClick(self):
        """This function is meant to be used in a Button, do not call this function directly"""
        if TileTemplate.selectedTile == self:
            TileTemplate.selectedTile = None
        else:
            TileTemplate.selectedTile = self

    def onIncreaseIdButtonClick(self):
        self.id += 1
        self.idText.changeText(str(self.id))

    def onDecreaseIdButtonClick(self):
        self.id -= 1
        self.idText.changeText(str(self.id))

    def changeId(self, newId):
        self.id = newId
        self.idText.changeText(str(newId))
    
    def onDeleteButtonClick(self):
        TileTemplate.removeTileTemplate(self)

    def setActiveAllGUIElements(self, isActive):
        self.button.isActive = isActive
        self.increaseIdButton.isActive = isActive
        self.decreaseIdButton.isActive = isActive
        self.idText.isActive = isActive
        self.deleteButton.isActive = isActive

    def __init__(self, texture, id, previewImg, texturePath):

        self.texture = texture
        self.id = id
        self.previewImg = previewImg
        self.texturePath = texturePath

        # GUI stuff
        guiPos = pygame.Vector2(80 + 72 * (len(TileTemplate.tiles) % TileTemplate.maxTileTemplateGUICount), 720)
        guiSize = pygame.Vector2(50, 50)
        guiIdButtonSize = pygame.Vector2(15, 15)
        
        self.button = GuiLib.Button(guiPos, guiSize, self.texture, self.onClick)
        
        self.increaseIdButton = GuiLib.Button(guiPos + pygame.Vector2(20, 32.5), guiIdButtonSize, TileTemplate.increaseIdButtonTexture, self.onIncreaseIdButtonClick)
        self.decreaseIdButton = GuiLib.Button(guiPos + pygame.Vector2(-20, 32.5), guiIdButtonSize, TileTemplate.decreaseIdButtonTexture, self.onDecreaseIdButtonClick)
        
        self.idText = GuiLib.Text(guiPos + pygame.Vector2(0, 42), 14, ROBOTO_REGULAR_PATH)
        self.idText.changeText(str(self.id))
        self.idText.changeBackgroundColor((230, 95, 85))
        self.idText.changeTextColor((255, 255, 255))

        self.deleteButton = GuiLib.Button(guiPos + pygame.Vector2(-15, -35), pygame.Vector2(20, 20), TileTemplate.deleteButtonTexture, self.onDeleteButtonClick)

        if len(TileTemplate.tiles) + 1 > TileTemplate.TemplateGUIStartRange + TileTemplate.maxTileTemplateGUICount:
            self.setActiveAllGUIElements(False)

        TileTemplate.tiles.append(self)

    @staticmethod
    def addTileTemplate(texturePath):
        """Use this function to create more tile templates instead of instancing TileTemplate class!"""
        newTileImg = pygame.image.load(texturePath).convert_alpha()
        newTileImgPreview = pygame.Surface((newTileImg.get_width(), newTileImg.get_height()), pygame.SRCALPHA)
        newTileImgPreview.set_alpha(128)
        newTileImgPreview.blit(newTileImg, pygame.Vector2(0, 0))
        # Create the new tile
        return TileTemplate(newTileImg, len(TileTemplate.tiles), newTileImgPreview, texturePath)

    @staticmethod
    def removeTileTemplate(templateToRemove):
        # Shift all gui elements to the left

        index = TileTemplate.tiles.index(templateToRemove)

        for i in range(index, len(TileTemplate.tiles)):
            TileTemplate.tiles[i].button.pos.x -= 60
            TileTemplate.tiles[i].increaseIdButton.pos.x -= 60
            TileTemplate.tiles[i].decreaseIdButton.pos.x -= 60
            TileTemplate.tiles[i].deleteButton.pos.x -= 60
            TileTemplate.tiles[i].idText.pos.x -= 60
            TileTemplate.tiles[i].idText.changeText(TileTemplate.tiles[i].idText.text)

        # Remove all GUI elements on the templateToRemove
        Tile.removeTileByTemplate(templateToRemove)
        GuiLib.GUI.removeElement(templateToRemove.button)
        GuiLib.GUI.removeElement(templateToRemove.idText)
        GuiLib.GUI.removeElement(templateToRemove.increaseIdButton)
        GuiLib.GUI.removeElement(templateToRemove.decreaseIdButton)
        GuiLib.GUI.removeElement(templateToRemove.deleteButton)
        TileTemplate.tiles.remove(templateToRemove)
        TileTemplate.selectedTile = None

    @staticmethod
    def findTileTemplateById(id): # I created this function instead of using a dictionary with id as key because the id of the tile could change very frequently, and constantly creating new dictionary elements with the new id would probably not be performant
        for tileTemplate in TileTemplate.tiles:
            if tileTemplate.id == id:
                return tileTemplate
        return None
    
class Camera: # camera class makes it easy to offset things drawn in pygame by the position of the camera.
    size = pygame.Vector2(0, 0) # currently the objects drawn by the camera do not scale with its size, this can be added later
    screen = None
    pos = pygame.Vector2(0, 0)
    
    @staticmethod
    def drawLine(color, start : pygame.Vector2, end : pygame.Vector2, width):
        """Draws a line based in world coordinates based on the start and end values given"""
        pygame.draw.line(screen, color, start + pygame.Vector2(-Camera.pos.x, Camera.pos.y) + pygame.Vector2(Camera.size.x / 2, Camera.size.y / 2), end + pygame.Vector2(-Camera.pos.x, Camera.pos.y) + pygame.Vector2(Camera.size.x / 2, Camera.size.y / 2), width)

    @staticmethod
    def drawBoxOutline(color, pos, size, lineWidth):
        """Draws the outline of a box in world coordinates based on the position, size and lineWidth given"""
        Camera.drawLine(color, pos + pygame.Vector2(-size.x / 2, size.y / 2), pos + pygame.Vector2(-size.x / 2, -size.y / 2), lineWidth)
        Camera.drawLine(color, pos + pygame.Vector2(-size.x / 2, -size.y / 2), pos + pygame.Vector2(size.x / 2, -size.y / 2), lineWidth)
        Camera.drawLine(color, pos + pygame.Vector2(size.x / 2, -size.y / 2), pos + pygame.Vector2(size.x / 2, size.y / 2), lineWidth)
        Camera.drawLine(color, pos + pygame.Vector2(size.x / 2, size.y / 2), pos + pygame.Vector2(-size.x / 2, size.y / 2), lineWidth)
    
    @staticmethod
    def getWorldMousePos(mousePos) -> pygame.Vector2:
        """Returns the position of the mouse in world coordinates"""
        mousePos += pygame.Vector2(Camera.pos.x, -Camera.pos.y)
        mousePos += pygame.Vector2(-Camera.size.x / 2, -Camera.size.y / 2)
        return mousePos
    
    @staticmethod
    def drawTexture(texture, pos, size = pygame.Vector2(-1, -1)):
        """Draws a texture in world coordinates, if the size is pygame.Vector2(-1, -1), the size of the original texture will be used"""
        if size != pygame.Vector2(-1, -1):
            texture = pygame.transform.scale(texture, size)
        Camera.screen.blit(texture, pos + pygame.Vector2(-Camera.pos.x, Camera.pos.y) + pygame.Vector2(Camera.size.x / 2, Camera.size.y / 2))

# ----------------------- initializing things -------------------
pygame.init()

screen = pygame.display.set_mode([1024, 768], pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
pygame.display.set_caption("David's Tilemap Editor")
running = True

Camera.size = pygame.Vector2(1024, 768)
Camera.screen = screen

GuiLib.GUI.initialize(screen)

# Making a panel for the tiles to be displayed on (this is for decoration)
tilePanel = GuiLib.Panel(pygame.Vector2(512, 720), pygame.Vector2(1024, 100), (230, 95, 85))

# must load the increase and decrease id buttons here because they cannot load before pygame.display is initialized
TileTemplate.increaseIdButtonTexture = pygame.image.load("img/plusButton2.png").convert_alpha()
TileTemplate.decreaseIdButtonTexture = pygame.image.load("img/minusButton.png").convert_alpha()
TileTemplate.deleteButtonTexture = pygame.image.load("img/trashIcon.png").convert_alpha()

#------------------------------- arrows for changing the row of tile templates ------------------------
rightArrowImg = pygame.image.load("img/RightArrow.png").convert_alpha()
leftArrowImg = pygame.image.load("img/LeftArrow.png").convert_alpha()

def moveTileTemplatesRightArrow():
    if TileTemplate.TemplateGUIStartRange + TileTemplate.maxTileTemplateGUICount < len(TileTemplate.tiles):
        TileTemplate.TemplateGUIStartRange += TileTemplate.maxTileTemplateGUICount
    for i in range(len(TileTemplate.tiles)):
        if i >= TileTemplate.TemplateGUIStartRange and i < TileTemplate.TemplateGUIStartRange + TileTemplate.maxTileTemplateGUICount:
            TileTemplate.tiles[i].setActiveAllGUIElements(True)
        else:
            TileTemplate.tiles[i].setActiveAllGUIElements(False)

def moveTileTemplatesLeftArrow():
    TileTemplate.TemplateGUIStartRange -= TileTemplate.maxTileTemplateGUICount
    TileTemplate.TemplateGUIStartRange = max(0, TileTemplate.TemplateGUIStartRange)
    for i in range(len(TileTemplate.tiles)):
        if i >= TileTemplate.TemplateGUIStartRange and i < TileTemplate.TemplateGUIStartRange + TileTemplate.maxTileTemplateGUICount:
            TileTemplate.tiles[i].setActiveAllGUIElements(True)
        else:
            TileTemplate.tiles[i].setActiveAllGUIElements(False)

tileTemplateMoveRightButton = GuiLib.Button(pygame.Vector2(930, 720), pygame.Vector2(36, 36), rightArrowImg, moveTileTemplatesRightArrow)
tileTemplateMoveLeftButton = GuiLib.Button(pygame.Vector2(22, 720), pygame.Vector2(36, 36), leftArrowImg, moveTileTemplatesLeftArrow)

#----------------------- Save Tiles Button ---------------------------
saveCompressed = True
def saveButtonFunc():
    print("Saving tilemap and templates...")
    if saveCompressed:
        SaveSystem.SaveTilemapCompressed(Tile.tilemap)
    else:
        SaveSystem.SaveTilemap(Tile.tilemap)
    SaveSystem.SaveTileTemplates(TileTemplate.tiles)

saveButtonImg = pygame.image.load("img/SaveIcon.png")
saveButton = GuiLib.Button(pygame.Vector2(30, 30), pygame.Vector2(40, 40), saveButtonImg, saveButtonFunc)

# Creating the tile compression toggle
compressionDescriptionText = GuiLib.Text(pygame.Vector2(230, 30), 16, ROBOTO_REGULAR_PATH)
compressionDescriptionText.changeText("Tilemap Compression: ")

tilemapCompButtonPanel = GuiLib.Panel(pygame.Vector2(350, 30), pygame.Vector2(60, 40), (60, 240, 99))
tilemapCompButtonText = GuiLib.Text(pygame.Vector2(350, 30), 16, ROBOTO_REGULAR_PATH)
tilemapCompButtonText.changeText("TRUE")
tilemapCompButtonText.changeBackgroundColor((60, 240, 99))

def tilemapCompressionToggleButtonFunc():
    global saveCompressed
    saveCompressed = not saveCompressed
    if saveCompressed:
        tilemapCompButtonText.changeText("TRUE")
        tilemapCompButtonPanel.changeColor((60, 240, 99))
        tilemapCompButtonText.changeBackgroundColor((60, 240, 99))
    else:
        tilemapCompButtonText.changeText("FALSE")
        tilemapCompButtonPanel.changeColor((230, 95, 85))
        tilemapCompButtonText.changeBackgroundColor((230, 95, 85))

tilemapCompButton = GuiLib.Button(pygame.Vector2(350, 30), pygame.Vector2(60, 40), None, tilemapCompressionToggleButtonFunc)

#----------------------- Load Tiles Button -----------------------------
def loadButtonFunc():
    print("Loading tilemap and templates...")
    # Loading the tile templates
    for t in TileTemplate.tiles: # Remove all tile templates so there are no duplicates
        TileTemplate.removeTileTemplate(t)

    tileTemplatesData = SaveSystem.LoadTileTemplates()
    for tileTemplateDataElement in tileTemplatesData: # parse the data
        if not os.path.isfile(tileTemplateDataElement["Path"]):
            print(f"Image path at {tileTemplateDataElement['Path']} is invalid!")
            continue
        t = TileTemplate.addTileTemplate(tileTemplateDataElement["Path"])
        t.changeId(tileTemplateDataElement["Id"])

    for i in range(len(Tile.tilemap)): # Clearing the tilemap
        for j in range(len(Tile.tilemap[i])):
            Tile.tilemap[i][j] = None
    

    # Loading the tilemap
    tilemapData = SaveSystem.LoadTilemap()

    if tilemapData[0]["IsCompressed"] == True:
        tilemapData.pop(0)
        for tileData in tilemapData:
            tileTemplate = TileTemplate.findTileTemplateById(tileData["Id"])
            if tileTemplate == None:
                print(f"Id: {tileData['Id']} does not exist! cannot load tile at ({pos.x}, {pos.y})")
                continue
            startPos = tileData["StartPosition"]
            endPos = tileData["EndPosition"]
            for i in range(startPos[0], endPos[0] + 1):
                for j in range(startPos[1], endPos[1] + 1):
                    pos = pygame.Vector2(i, j)
                    Tile.addTile(pos, tileTemplate)
    else:
        tilemapData.pop(0)
        for tileData in tilemapData: # parse the data
            tileTemplate = TileTemplate.findTileTemplateById(tileData["Id"])
            if tileTemplate == None:
                print(f"Id: {tileData['Id']} does not exist! cannot load tile at ({pos.x}, {pos.y})")
                continue
            pos = pygame.Vector2(tileData["Position"][0], tileData["Position"][1])
            Tile.addTile(pos, tileTemplate)

    print("Finished loading tilemap")

loadButtonImg = pygame.image.load("img/LoadIcon.png")
loadButton = GuiLib.Button(pygame.Vector2(90, 30), pygame.Vector2(40, 40), loadButtonImg, loadButtonFunc)

# ---------------------------- Add Tile Button --------------------
def addTileFunc():
    filePath = filedialog.askopenfilename(initialdir="/", title="select an image for new tile", filetypes=(("all files", "*.*"), ("JPG File","*.jpg*"), ("PNG File","*.png*")))

    if os.path.isfile(filePath):
        try:
            TileTemplate.addTileTemplate(filePath)
        except:
            print("Unsupported image format!")

addTileButtonImg = pygame.image.load("img/PlusButton.png")
addTileButton = GuiLib.Button(pygame.Vector2(980, 720), pygame.Vector2(50, 50), addTileButtonImg, addTileFunc)

#-------------------- MAIN LOOP -------------------------
mouseLeftButtonHeld = False # a bool to store if the left mouse button is held down
mouseRightButtonHeld = False # a bool to store if the right mouse button is held down

clock = pygame.time.Clock()
deltaTime = 0 # time in seconds between each frame

while running:
    deltaTime = clock.tick() / 1000

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouseLeftButtonHeld = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouseLeftButtonHeld = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mouseRightButtonHeld = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            mouseRightButtonHeld = False

    # Fill the background with grey
    screen.fill((255, 255, 255))

    # get input
    keys = pygame.key.get_pressed()
    cameraSpeed = 0
    fastCameraSpeed = 800
    normalCameraSpeed = 400
    if keys[pygame.K_LSHIFT]: # increase the camera speed if the left shift key is pressed
        cameraSpeed = fastCameraSpeed
    else:
        cameraSpeed = normalCameraSpeed

    if keys[pygame.K_w]: # move the camera based on user input
        Camera.pos.y += cameraSpeed * deltaTime
    if keys[pygame.K_s]:
        Camera.pos.y -= cameraSpeed * deltaTime
    if keys[pygame.K_d]:
        Camera.pos.x += cameraSpeed * deltaTime
    if keys[pygame.K_a]:
        Camera.pos.x -= cameraSpeed * deltaTime

    # Mouse input
    screenMousePos = pygame.mouse.get_pos()
    screenMousePos = pygame.Vector2(screenMousePos[0], screenMousePos[1]) # must convert to a vector2
    positionIsOnGUI = GuiLib.GUI.positionIsOnGUI(screenMousePos)

    mousePos = Camera.getWorldMousePos(screenMousePos)
    mousePos = pygame.Vector2(round(mousePos.x / GRID_SIZE) * GRID_SIZE, round(mousePos.y / GRID_SIZE) * GRID_SIZE) - pygame.Vector2(GRID_SIZE / 2, GRID_SIZE / 2)
    selectedTileGridPos = pygame.Vector2(int((mousePos.x + GRID_SIZE / 2) / GRID_SIZE), int((mousePos.y + GRID_SIZE / 2) / GRID_SIZE))
    # draw a preview of the tile at the mouse poisition if it is selected
    if TileTemplate.selectedTile != None and (not positionIsOnGUI):
        Camera.drawTexture(TileTemplate.selectedTile.previewImg, mousePos, pygame.Vector2(30, 30))
        if mouseLeftButtonHeld:
            Tile.addTile(selectedTileGridPos, TileTemplate.selectedTile)

    if not positionIsOnGUI and mouseRightButtonHeld:
        # Removing tiles
        Tile.removeTileAtPos(selectedTileGridPos)

    # ------------------------- draw the grid ----------------------
    width = GRID_COLUMN_COUNT * GRID_SIZE
    height = GRID_ROW_COUNT * GRID_SIZE
    gridColor = "#b8c7de"
    for i in range(0, GRID_COLUMN_COUNT + 1): # draw thicker lines every 3 tiles
        if(i % 3 == 0):
            Camera.drawLine(gridColor, pygame.Vector2(i * GRID_SIZE, 0) - pygame.Vector2(GRID_SIZE / 2, GRID_SIZE / 2), pygame.Vector2(i * GRID_SIZE, height) - pygame.Vector2(GRID_SIZE / 2, GRID_SIZE / 2), 2)
        else:
            Camera.drawLine(gridColor, pygame.Vector2(i * GRID_SIZE, 0) - pygame.Vector2(GRID_SIZE / 2, GRID_SIZE / 2), pygame.Vector2(i * GRID_SIZE, height) - pygame.Vector2(GRID_SIZE / 2, GRID_SIZE / 2), 1)
    for i in range(0, GRID_ROW_COUNT + 1):
        if(i % 3 == 0):
            Camera.drawLine(gridColor, pygame.Vector2(0, i * GRID_SIZE) - pygame.Vector2(GRID_SIZE / 2, GRID_SIZE / 2), pygame.Vector2(width, i * GRID_SIZE) - pygame.Vector2(GRID_SIZE / 2, GRID_SIZE / 2), 2)
        else:
            Camera.drawLine(gridColor, pygame.Vector2(0, i * GRID_SIZE) - pygame.Vector2(GRID_SIZE / 2, GRID_SIZE / 2), pygame.Vector2(width, i * GRID_SIZE) - pygame.Vector2(GRID_SIZE / 2, GRID_SIZE / 2), 1)


    Tile.drawAllTiles()
    # GUI functions
    GuiLib.GUI.drawElements()
    GuiLib.GUI.checkInput(events)
    # Did the user click the window close button?
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # Flip the display
    pygame.display.flip()
# Done! Time to quit.
pygame.quit()
sys.exit()