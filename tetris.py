import pygame
import sys
import random
import time
from pygame.locals import *
import easygui as eg
from copy import deepcopy
from pygame import Rect
import os
pygame.init()

black=(0,0,0)
white=(255,255,255)
green=(0,255,0)
red=(255,0,0)
blue=(0,0,255)
grey=(128, 128, 128)
aqua=(0,255,255)
fuchsia=(255,0,255)
maroon=(128,0,0)
purple=(128,0,128)
orange=(255,128,0)
yellow=(255,255,0)
navy=(0,0,128)
red1=(170,0,0)
aqua1=(0,170,170)
yellow1=(170,170,0)
blue1=(0,0,170)
orange1=(170,85,0)
green1=(0,170,0)
purple1=(85,0,85)
grey1=(85,85,85)


square=20
leftbar=6
topbar=4
bottombar=1
pscreenw=10
pscreenh=25
screenw=pscreenw+leftbar*2
screenh=pscreenh+topbar+bottombar
extratime=1200
holdboxsize=4
nextshapeboxwidth=5
nextshapeboxheight=12
timeincrease=500
heldshape=0



atts={
    'i':(aqua,[(0,0),(1,0),(2,0),(3,0)],Rect(3, -1, 4, 1)),
    'o':(yellow,[(0,0),(1,0),(0,1),(1,1)],Rect(4, -2, 2, 2)),
    'j':(blue,[(0,0),(1,0),(2,0),(2,1)],Rect(3, -2, 3, 2)),
    'l':(orange,[(0,0),(1,0),(2,0),(0,1)],Rect(3, -2, 3, 2)),
    's':(green,[(1,0),(2,0),(0,1),(1,1)],Rect(3, -2, 3, 2)),
    't':(purple,[(1,0),(0,1),(1,1),(2,1)],Rect(3, -2, 3, 2)),
    'z':(red,[(0,0),(1,0),(1,1),(2,1)],Rect(3, -2, 3, 2)),
    'b':(white,[(x,0) for x in range(pscreenw)],Rect(0,pscreenh,pscreenw,1))
    }

colours1={
    aqua:aqua1,
    yellow:yellow1,
    blue:blue1,
    orange:orange1,
    green:green1,
    purple:purple1,
    red:red1,
    white:white
    }

shapes='iojlstz'

directions={
    'up':(0,-1),
    'down':(0,1),
    'left':(-1,0),
    'right':(1,0)
    }

screen=pygame.display.set_mode(((screenw)*square,(screenh)*square))


class Shape(pygame.sprite.Sprite):
    def draw_squares(self,bottom):
        if self.letter!='b':
            for coord in self.ghost(bottom):
                x,y,colour = coord
                pygame.draw.rect(self.pscreen,grey1,[x*square,y*square,square,square],0)
                pygame.draw.rect(self.pscreen,white,[x*square,y*square,square,square],1)

        for coord in self.abs_coords():        
            x,y,colour = coord
            colour1=colours1[colour]
            pygame.draw.rect(self.pscreen,colour,[x*square,y*square,square,square],0)
            pygame.draw.rect(self.pscreen,colour1,[x*square+2,y*square+2,square-4,square-4],4)
            pygame.draw.rect(self.pscreen,white,[x*square,y*square,square,square],1)
                
    def ghost(self,bottom):
        orig_rect=(self.rect.left,self.rect.top,self.rect.width,self.rect.height)
        while not self.will_intersect(bottom,'down'):
            self.rect.top+=1
        absolute=self.abs_coords()
        self.rect.left=orig_rect[0]
        self.rect.top=orig_rect[1]
        self.rect.width=orig_rect[2]
        self.rect.height=orig_rect[3]
        return absolute
        
    def __init__(self,letter,pscreen):
        self.letter=letter
        colour,self.coords,self.rect = deepcopy(atts[letter])
        for i in range(len(self.coords)):
            x,y=self.coords[i]
            self.coords[i]=(x,y,colour)
        self.pscreen=pscreen
        #self.draw_squares(bottom)
        self.next_update_time = 0
        self.fixedcheck=0
        self.state='Moving'
        self.score=0
        self.timeincrease=timeincrease
    def update(self,current_time,other):
        if self.next_update_time < current_time:
            if not self.will_intersect(other,'down'):
                self.rect.top+=1
            self.next_update_time=current_time+other.timeincrease
        if self.fixedcheck<current_time:
            if self.will_intersect(other,'down'):
                self.state='Fixed'
                self.glue(other)
            self.fixedcheck=current_time+extratime
            self.extend=False
    def rotate(self,bottom):
        orig_centre=(self.rect.left+int(self.rect.width/2),self.rect.top+int(self.rect.height/2))
        self.rect=Rect(self.rect.left,self.rect.top,self.rect.height,self.rect.width)
        for i in range(len(self.coords)):
            x, y, colour = self.coords[i]
            self.coords[i] = (-y+self.rect.width-1,x,colour)
        new_centre=(self.rect.left+int(self.rect.width/2),self.rect.top+int(self.rect.height/2))
        x_diff=orig_centre[0]-new_centre[0]
        y_diff=orig_centre[1]-new_centre[1]
        if orig_centre!=new_centre:
          self.rect.left+=x_diff
          self.rect.top+=y_diff  
        while self.rect.right>pscreenw:
            self.rect.left-=1
        while self.rect.left<0:
            self.rect.left+=1
        while self.check_intersect(bottom):
            self.rect.top-=1    
        self.draw_squares(bottom)
    def check_intersect(self,other):
        for sc in self.abs_coords():
            for oc in other.abs_coords():
                if sc[0] == oc[0] and sc[1] == oc[1]:
                    return True
        return False
    def abs_coords(self):
        absolute=[]
        for coord in self.coords:
            absolute+=[(self.rect.left+coord[0],self.rect.top+coord[1],coord[2])]
        return absolute
    def will_intersect(self,other,direction):
        top=self.rect.top
        left=self.rect.left
        self.rect.left+=directions[direction][0]
        self.rect.top+=directions[direction][1]
        if self.check_intersect(other):
            self.rect.top=top
            self.rect.left=left
            return True
        self.rect.top=top
        self.rect.left=left
        return False
    def glue(self,bottom):
        if self.state=='Fixed':
            original=self.rect.topleft
            if self.rect.top<bottom.rect.top:
                difference=bottom.rect.top-self.rect.top
                bottom.rect.height=bottom.rect.bottom-self.rect.top
                bottom.rect.top=self.rect.top
                for item in range(len(bottom.coords)):
                    x,y,colour = bottom.coords[item]
                    bottom.coords[item]=(x,y+difference,colour)
            new=bottom.rect.topleft
            add_x=original[0]-new[0]
            add_y=original[1]-new[1]
            for item in range(len(self.coords)):
                x,y,colour=self.coords[item]
                self.coords[item]=(x+add_x,y+add_y,colour)
            bottom.coords+=self.coords
            bottom.check_rows()
            bottom.draw_squares(bottom)
    def check_rows(self):
        rows_to_collapse=[]
        for row in range(self.rect.height-1):
            row_x=set()
            for x in self.coords:
                if x[1]==row:
                    row_x.add(x[0])
            if len(row_x)==self.rect.width:
                rows_to_collapse.append(row)
        if len(rows_to_collapse)==1:
            self.score+=1
        elif len(rows_to_collapse)==2:
            self.score+=3
        elif len(rows_to_collapse)==3:
            self.score+=5
        elif len(rows_to_collapse)==4:
            self.score+=8
        for row in reversed(rows_to_collapse):
            self.rect.height-=1
            self.rect.top+=1
            new_coords=[]
            for i,coord in enumerate(self.coords):
                x,y,colour=coord
                if y<row:
                    new_coords.append(coord)
                elif y>row:
                    new_coords.append((x,y-1,colour))
            self.coords=new_coords
        self.timeincrease-=len(rows_to_collapse)*2
                            
            
def pause():

    pause = eg.buttonbox("PAUSED\n\nControls:\nUP: Rotate\nSPACE: Hard drop\nP or ENTER: Pause\nSHIFT: Hold\n\nWould you like to continue?",choices=('Continue','Quit'))
    pygame.mixer.music.unpause()
    return pause
 

def end():
    return eg.ynbox("Sorry, you lost! Would you like to try again?", "Sorry!") 

def title(screen):
    screen.fill(grey)
    logo = pygame.image.load(os.path.join('tetris.png'))
    screen.blit(logo, ((screenw*square-logo.get_width())/2,50))

    font=pygame.font.Font(None,20)
    text1=font.render("Controls:",1,white)
    text2=font.render("UP: Rotate",1,white)
    text3=font.render("SPACE: Hard drop",1,white)
    text4=font.render("P or ENTER: Pause",1,white)
    text5=font.render("SHIFT: Hold",1,white)
    text6=font.render("M: Mute",1,white)
    text7=font.render("PRESS ANY KEY TO CONTINUE",1,white)
    screen.blit(text1,((screenw*square-text1.get_width())/2,100+logo.get_height()))
    screen.blit(text2,((screenw*square-text2.get_width())/2,110+logo.get_height()+text1.get_height()))
    screen.blit(text3,((screenw*square-text3.get_width())/2,120+logo.get_height()+text1.get_height()*2))
    screen.blit(text4,((screenw*square-text4.get_width())/2,130+logo.get_height()+text1.get_height()*3))
    screen.blit(text5,((screenw*square-text5.get_width())/2,140+logo.get_height()+text1.get_height()*4))
    screen.blit(text6,((screenw*square-text6.get_width())/2,150+logo.get_height()+text1.get_height()*5))
    screen.blit(text7,((screenw*square-text7.get_width())/2,170+logo.get_height()+text1.get_height()*6))

    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                if event.key==27:
                    return False
                else:
                    return True

    
            
            
def game():
    pygame.key.set_repeat(300, 100)
#440 #320
    screen.fill(grey)
    pygame.display.set_caption('Tetris')

    heldshape=None

    font = pygame.font.Font(None, 36)
    
    holdbox=pygame.Surface((holdboxsize*square,holdboxsize*square))
    holdbox.fill(black)

    pscreen=pygame.Surface((pscreenw*square,pscreenh*square))
    pscreen.fill(black)

    nextshapelist=[]
    nextshapelist.append(random.choice(shapes))
    nextshapelist.append(random.choice(shapes))
    nextshapelist.append(random.choice(shapes))

    nextshapebox=pygame.Surface((nextshapeboxwidth*square,nextshapeboxheight*square))
    nextshapebox.fill(black)

    pygame.display.flip()
    bottom=Shape('b',pscreen)
    z=Shape(random.choice(shapes),pscreen)
    z.draw_squares(bottom)

    alive=True
    nexttime=0

    hold=True
    mute=False

    while alive:
        time=pygame.time.get_ticks()        
        extend=False
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                #109
                if event.key==27:
                    return False
                elif event.key==109:
                    if mute:
                        pygame.mixer.music.set_volume(0.9921875)
                        mute=False
                    else:
                        pygame.mixer.music.set_volume(0.0)
                        mute=True
                elif event.key in (303,304) and hold:
                    hold=False
                    if not heldshape:
                        heldshape=z
                        z = Shape(nextshapelist.pop(0),pscreen) #new shape
                        nextshapelist.append(random.choice(shapes))
                        heldshape.rect=deepcopy(atts[heldshape.letter][2])
                    else:
                        z1=z
                        z=heldshape
                        heldshape=z1
                        heldshape.rect=deepcopy(atts[heldshape.letter][2])

                elif event.key==276 and z.rect.left!=0 and not z.state=='Fixed' and not z.will_intersect(bottom,'left'):
                    z.rect.left-=1 #move left
                    z.fixedcheck=time+extratime
                elif event.key==275 and z.rect.right!=pscreenw and not z.state=='Fixed' and not z.will_intersect(bottom,'right'):
                    z.rect.left+=1 #move right
                    z.fixedcheck=time+extratime
                elif event.key==274 and not z.will_intersect(bottom,'down') and not z.state=='Fixed':
                    z.rect.top+=1 #move down
                elif event.key==32: 
                    while not z.will_intersect(bottom,'down'):
                        z.rect.top+=1 #hard drop
                    z.state='Fixed'
                    z.fixedcheck=0
                elif event.key==273:
                    z.rotate(bottom) #rotate
                    z.fixedcheck=time+extratime
                elif event.key==13 or event.key==112: #pause
                    pygame.mixer.music.pause()
                    if not title(screen):
                        return False
                    pygame.mixer.music.unpause()
            if event.type==pygame.QUIT:
                return False


        score=str(bottom.score)
        pscreen.fill(black)
        screen.fill(grey)
        nextshapebox.fill(black)
        for shape in range(len(nextshapelist)):
            newshape=Shape(nextshapelist[shape],pscreen)
            for coord in newshape.coords:        
                x,y,colour = coord
                colour1=colours1[colour]
                pygame.draw.rect(nextshapebox,colour,[((nextshapeboxwidth-newshape.rect.width)/2+x)*square,(y*square+square/2)+shape*80,square,square],0)
                pygame.draw.rect(nextshapebox,colour1,[(((nextshapeboxwidth-newshape.rect.width)/2+x)*square)+2,((y*square+square/2)+shape*80)+2,square-4,square-4],4)
                pygame.draw.rect(nextshapebox,white,[((nextshapeboxwidth-newshape.rect.width)/2+x)*square,(y*square+square/2)+shape*80,square,square],1)
        holdbox.fill(black)
        if heldshape:
            newshape=Shape(heldshape.letter,pscreen)
            for coord in newshape.coords:
                x,y,colour=coord
                colour1=colours1[colour]
                pygame.draw.rect(holdbox,colour,[((holdboxsize-newshape.rect.width)/2+x)*square,((holdboxsize-newshape.rect.height)/2+y)*square,square,square],0)
                pygame.draw.rect(holdbox,colour1,[((holdboxsize-newshape.rect.width)/2+x)*square+2,((holdboxsize-newshape.rect.height)/2+y)*square+2,square-4,square-4],4)
                pygame.draw.rect(holdbox,white,[((holdboxsize-newshape.rect.width)/2+x)*square,((holdboxsize-newshape.rect.height)/2+y)*square,square,square],1)

        #Keeping score - still to fix!
                
        #scoretitleimage=font.render('SCORE:',1,white)
        #scoretitlepos=((screenw*square-scoretitleimage.get_width())/2,square)
        #screen.blit(scoretitleimage,scoretitlepos)

        #scoretextimage = font.render(score,1,white)
        #scoretextpos=((screenw*square-scoretextimage.get_width())/2,square+scoretitleimage.get_height()+5)
        #screen.blit(scoretextimage,scoretextpos)
        
        z.draw_squares(bottom)
        bottom.draw_squares(bottom)
        z.update(time,bottom)
        
        screen.blit(pscreen,(leftbar*square,topbar*square,pscreenw*square,pscreenh*square))
        screen.blit(holdbox,(square,topbar*square,holdboxsize*square,holdboxsize*square))
        screen.blit(nextshapebox,((leftbar+pscreenw)*square+((leftbar-nextshapeboxwidth)*square)/2,topbar*square))

        pygame.display.update()
        if bottom.rect.top<=0:
            return True #lose the game
        if z.state=='Fixed':
            z = Shape(nextshapelist[0],pscreen) #new shape
            del nextshapelist[0]
            nextshapelist.append(random.choice(shapes))
            hold=True

def main():
    pygame.mixer.music.load('tetris.mp3')
    pygame.mixer.music.play(-1)
    if not title(screen):
        return
    while True:
        if not game():
            break
        if not end():
            break
        

main()
pygame.quit()
