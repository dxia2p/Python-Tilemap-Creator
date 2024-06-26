import pygame
import sys

class GUIBase: # do not have overlapping GUI elements. this will cause strange behaviour
    def __init__(self, rect : pygame.Rect) -> None:
        GUI.addElement(self)
        self.rect = rect
        self.isActive = True
        pass

    def draw(self):
        if not self.isActive:
            return
        pass
    
    def checkInput(self, event):
        if not self.isActive:
            return
        pass

    def checkPositionIsInElement(self, position : pygame.Vector2) -> bool:
        """Checks if the given position is inside the rect of this element"""
        if position.x < self.rect.right and position.x > self.rect.left and position.y > self.rect.top and position.y < self.rect.bottom:
            return True
        return False

class GUI: # a class to store information about all the GUI elements
    elements = []
    surface = None
    mouseUpEventUsed = False

    @staticmethod
    def initialize(surface):
        GUI.surface = surface
    
    @staticmethod
    def drawElements(): # this function needs to be called every frame to draw all the GUI elements
        for element in GUI.elements:
            element.draw()
    
    @staticmethod
    def checkInput(events):
        GUI.mouseUpEventUsed = False
        for element in GUI.elements:
            element.checkInput(events)

    @staticmethod
    def addElement(element : GUIBase): # must be called every time a GUI element is created
        GUI.elements.append(element)

    @staticmethod
    def positionIsOnGUI(position):
        """
        Checks if the position given overlaps with any GUI element. This can be useful for preventing the user from performing actions in a game while clicking on the UI.
        """
        for element in GUI.elements:
            if element.checkPositionIsInElement(position):
                return True
        return False

    @staticmethod
    def removeElement(element):
        GUI.elements.remove(element)   


class Button (GUIBase): # This is a simple button which can detect clicks within its rectangular bounding box
    def __init__(self, pos : pygame.Vector2, size : pygame.Vector2, texture, func) -> None:
        rect = pygame.Rect(pos.x - size.x / 2, pos.y - size.y / 2, size.x, size.y)
        GUIBase.__init__(self, rect)
        self.size = size
        self.originalSize = size
        self.pos = pos
        self.func = func
        self.originalTexture = None
        self.largerTexture = None
        self.texture = texture
        if texture != None:
            self.originalTexture = pygame.transform.scale(texture, self.size)
            self.largerTexture = pygame.transform.scale(texture, self.size * 1.15)
    
    def draw(self): # draw function which overrides GUIBase's draw function

        if not self.isActive:
            return

        if self.texture == None: # Draw a pink rectangle in case of missing texture
            #rect = pygame.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
            #rect.center = self.pos
            #pygame.draw.rect(self.surface, "pink", rect)
            pass
        else: # Draw the texture normally
            GUI.surface.blit(self.texture, self.pos - (self.size / 2))

    def checkInput(self, event):

        if not self.isActive:
            return

        p = pygame.mouse.get_pos()
        mousePos = pygame.Vector2(p[0], p[1])
        
        left = self.pos.x - self.size.x / 2
        right = self.pos.x + self.size.x / 2
        top = self.pos.y - self.size.y / 2
        bottom = self.pos.y + self.size.y / 2
        if mousePos.x > left and mousePos.x < right and mousePos.y < bottom and mousePos.y > top and (not GUI.mouseUpEventUsed):
            self.size = self.originalSize * 1.15
            self.texture = self.largerTexture
            for ev in event:
                if ev.type == pygame.MOUSEBUTTONUP: # Check if mouse input is within the rect of the button
                    self.func()
                    GUI.mouseUpEventUsed = True
        else:
            self.size = self.originalSize
            self.texture = self.originalTexture


class Text (GUIBase): # a text renderer, the functions are pretty self-explanatory
    def __init__(self, pos, fontSize, fontPath):
        
        self.pos = pos
        self.font = pygame.font.Font(fontPath, fontSize)
        self.text = ""
        self.textColor = (0, 0, 0)
        self.backgroundColor = (255, 255, 255)
        self.textRender = self.font.render(self.text, True, self.textColor, self.backgroundColor) # text render is the pygame object for text, while text is a string of text
        
        rect = self.textRender.get_rect()
        GUIBase.__init__(self, rect)
    
    def changeTextColor(self, newTextColor):
        self.textColor = newTextColor
        self.textRender = self.font.render(self.text, True, self.textColor, self.backgroundColor)

    def changeBackgroundColor(self, newBackgroundColor):
        self.backgroundColor = newBackgroundColor
        self.textRender = self.font.render(self.text, True, self.textColor, self.backgroundColor)

    def changeText(self, newText):
        self.text = newText
        self.textRender = self.font.render(self.text, True, self.textColor, self.backgroundColor)
        width = self.textRender.get_rect().width
        height = self.textRender.get_rect().height
        self.rect.center = pygame.Vector2(self.pos.x - width / 2, self.pos.y - height / 2)

    def draw(self):
        if not self.isActive:
            return
        GUI.surface.blit(self.textRender, self.rect)

class Panel (GUIBase): # just a colored rectangle
    def __init__(self, pos, size, color):
        rect = pygame.Rect(pos.x - size.x / 2, pos.y - size.y / 2, size.x, size.y)
        GUIBase.__init__(self, rect)
        self.pos = pos
        self.size = size
        self.color = color
    
    def draw(self):
        if not self.isActive:
            return
        pygame.draw.rect(GUI.surface, self.color, pygame.Rect(self.pos.x - self.size.x / 2, self.pos.y - self.size.y / 2, self.size.x, self.size.y))
    
    def changeColor(self, newColor):
        self.color = newColor