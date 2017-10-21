from random import random as rnd
from numpy import zeros 
import pygame 
from pygame.locals import *

FAIL=-1
NONE=0
WIN=1

class Field:
    def __init__(self,size,mines,maxmines,radius,safemode,shape):
        self.status=NONE
        self.safemode = False
        self.cell=zeros(size,dtype=int)
        self.mask=zeros(size,dtype=int)
        self.flag=zeros(size,dtype=int)
        self.mine=zeros(size,dtype=int)
        self.maxmines=maxmines
        self.radius=radius
        self.size=size
        self.shape=shape
        self.safemode=safemode
        m,n=size
        while mines>0:
            i=int(m*rnd())
            j=int(n*rnd())
            # print i,j,m,n 
            if self.mine[i][j]<self.maxmines: 
                mines-=self.putmine(i,j,1)

    def out(self,i,j):
        m,n=self.size
        if i<0 or j<0 : return True
        if i>=m or j>=n: return True
        return False  

    def rad(self,i,j,r):
        l=[]
        for ii in range(i-r,i+r+1):
            for jj in range(j-r,j+r+1):
                if not self.out(ii,jj):
                    l.append((ii,jj))
        return l
    
    def putmine(self,i,j,b):
        self.mine[i][j]+=b
        for ii,jj in self.rad(i,j,self.radius):
            self.cell[ii][jj]+=b
        return b

    def putflag(self,i,j):
        r=self.cell[i][j]
        s=0
        for ii,jj in self.rad(i,j,self.radius):
            r-=self.flag[ii][jj]
            if self.mask[ii][jj]==0 and self.flag[ii][jj]==0 : 
                s+=1
                i,j=ii,jj
        if s==1:
            self.flag[i][j]=r


    def change(self,i,j):
        if  self.flag[i][j] or self.out(i,j) :
            return
        self.mask[i][j]=1
        r=self.rad(i,j,self.radius)
        if self.cell[i][j]==sum([self.flag[ii][jj] for ii,jj in r]): 
            for ii,jj in r: 
                if self.mask[ii][jj]==0: self.change(ii,jj)

        if self.mine[i][j]:
            if self.safemode :
                mines=0
                for ii,jj in r:
                    mines-=self.putmine(ii,jj,-self.mine[ii][jj]) 
                    self.flag[ii][jj]=0
                while mines>0:
                    ii,jj = r[int(rnd()*len(r))]
                    if self.mine[ii][jj]<self.maxmines: 
                        mines-=self.putmine(ii,jj,1)
                for ii,jj in self.rad(i,j,2*self.radius):
                    self.mask[ii][jj]=0
            else : 
                self.mask[:][:]=1

    def update(self):
        p=self.size[0]/2
        for i,j in self.rad(p,p,p):
            if self.mine[i][j]!=self.flag[i][j] or (self.mine[i][j]==0 and self.mask[i][j]==0):
                self.status=NONE
                return
            if self.mine[i][j]>0 and self.mask[i][j]>0:
                self.status=FAIL
                return
        else:
            self.status=WIN
            return
            
if True: # field init
    m,n=raw_input(" What are field dimensions? (two integers n and m) : ").split()
    m,n=max(int(n),int(m)),min(int(m),int(n))
    mines=int(raw_input(" How many bombs are there? (up to n*m) : "))
    radius=int(raw_input(" How far does a tile see? (in the classical case it's 1) : "))
    maxmines=int(raw_input(" What is the maximum number of mines within one square? (if 0 - no limit ) : "))
    if maxmines<1: maxmines=mines
    safemode={'y':1,'n':0}[raw_input(" Safe mode? (y/n) : ")[0]]
    field=Field((m,n),mines,maxmines,radius,safemode,0)
    

if True: # pygame init
    pygame.init()
    cell_height=min(1100/m,700/n)
    cell_width=int(cell_height*1.182)
    display_width = m*cell_width
    display_height = n*cell_height
    screen = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption('MineSweaper')

if True: # text init
    # fonts= pygame.font.get_fonts()
    # font=fonts[int(rnd()*len(fonts))];print font
    font = "freemono"
    colorCell=(0,250,0)
    colorFlag=(0,0,250)
    colorMine=(250,0,0)
    colorText=(250,250,0)
    colorTile=(250,250,170)
    colorFill=(0,0,90)
    fontNumber = pygame.font.SysFont(font, cell_height-1)
    fontText = pygame.font.SysFont(font, display_width/8)
    numCell = [ fontNumber.render(str(i), 1, colorCell) for i in range(100) ]
    numMine = [ fontNumber.render(str(i), 1, colorMine) for i in range(100) ]
    numFlag = [ fontNumber.render(str(i), 1, colorFlag) for i in range(100) ]
    textRE = fontText.render(" R - REPLAY ", 1, colorText)
    textGO = fontText.render(" Game OVER! ", 1, colorText)
    textYW = fontText.render("  You WIN!  ", 1, colorText)
    textNN = fontText.render(" ", 1, colorText)
    


def pos(i,j):
    return (cell_width*i,cell_height*j)

def coords(pos):
    return (pos[0]/cell_width,pos[1]/cell_height)
    
def drawfield():
    screen.fill(colorFill)
    for i,j in field.rad(m/2,m/2,m/2):
        p=pos(i,j)
        if field.mask[i][j]:
            if field.mine[i][j]: screen.blit(numMine[field.mine[i][j]], p)
            else: screen.blit(numCell[field.cell[i][j]], p)  
        else:
            pygame.draw.rect(screen,colorTile,p+(cell_width-2,cell_height-2),0)
            if field.flag[i][j]: screen.blit(numFlag[field.flag[i][j]], p) 
    screen.blit({WIN:textYW, FAIL:textGO, NONE:textNN}[field.status], (0,0))   
    if field.status!=NONE : screen.blit(textRE, (0,display_height/2))   
        

while 1: # Game loop
    field.update()
    drawfield()
    for event in pygame.event.get():
        if event.type == QUIT :
            print event, event.type
            pygame.quit()
            quit()
        if event.type == MOUSEBUTTONDOWN:
            i,j=coords(event.pos)
            if event.button == 1:
                if  field.flag[i][j]: field.flag[i][j]-=1
                else: field.change(i,j)
            if event.button == 3:
                if  field.mask[i][j]==0: field.flag[i][j]+=1
                else: field.putflag(i,j)
            field.update()
        if event.type == KEYDOWN:
            i,j=coords(pygame.mouse.get_pos())
            if  event.key==K_w :
                if  field.flag[i][j]: field.flag[i][j]-=1
                else: field.change(i,j)
            if  event.key==K_q :
                if  field.mask[i][j]==0: field.flag[i][j]+=1
                else: field.putflag(i,j)
            if event.key==K_r : 
                field=Field((m,n),mines,maxmines,radius,safemode,0)
            if event.key == K_ESCAPE : 
                pygame.quit()
                quit() 

    pygame.display.update()

