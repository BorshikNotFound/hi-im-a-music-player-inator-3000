# THE "hi im totally spotify"-INATOR 3000
# if ur reading this at 3 AM, go to sleep. python is not that important what are u doing

import vlc
from PySide6 import QtWidgets, QtCore, QtGui
import os
import random
import time
import colorsys
from PIL import Image as img

# path nonsense
PATH = __file__[:-9]
MUSICPATH = PATH + r"/songs"
LYRICSPATH = MUSICPATH + r"/lyrics"
ICONPATH = PATH + r"/assets"
PLAYLISTPATH = PATH + r"/playlists"

# vlc go brrrrrr
player = None
paused = False
volume = 100
prevvolume = 100
progress = 0
shuffling = False
repeating = False

# gui bullshit
maincolor = [120, 120, 120]
font = QtGui.QFont("Montserrat")

# the "what song is next" bullshit
playorder = []
where = 0

# get songs AND playlists
songs = {}
playlists = []
with open(f"{MUSICPATH}/songs.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    
    for song in lines:
        song = song.strip()
        items = song.split("#")
        filename, name, icon = items[0], items[1], items[2]
        
        songs[f"{MUSICPATH}/{filename}"] = [name, icon]
for file in os.listdir(PLAYLISTPATH):
    if not file.endswith(".txt"):
        print("are u stupid")
        continue
    
    playlist = []
    with open(f"{PLAYLISTPATH}/{file}", "r", encoding="utf-8") as f:
        lines = f.readlines()
        name, image = lines[0].strip(), lines[1].strip()
        
        playlist.append(name)
        playlist.append(image)
        
        contents = []
        for x in range(2, len(lines)):
            contents.append(lines[x].strip())
        
        playlist.append(contents)
    playlists.append(playlist)

# grab stuff from cache
with open(f"{PATH}/cache.txt", "r", encoding="utf-8") as f:
    for line in f.readlines():
        line = line.strip()
        args = line.split("=")
        
        if len(args) < 2: continue
        
        if args[0] == "color":
            values = args[1].split()
            result = []
            for x in values:
                result.append(int(x))
            maincolor = result
        if args[0] == "volume":
            volume = int(args[1])
        if args[0] == "progress":
            progress = int(args[1])
        if args[0] == "prevvolume":
            prevvolume = int(args[1])
        if args[0] == "shuffle":
            shuffling = bool(int(args[1]))
        if args[0] == "repeat":
            repeating = bool(int(args[1]))
        if args[0] == "playorder":
            playorder = args[1].split("#")

# play the song
def play (song):
    global player
    global paused
    
    if player is not None: player.stop()
    player = vlc.MediaPlayer(song)
    player.play()
    player.audio_set_volume(volume)
    
    paused = False

# pause the song? maybe???? why are u asking me what this does are u stupid
def pause ():
    global paused
    if player is not None:
        player.pause()
        paused = not paused

# save the FUCKING PLAYLIST WHAT ARE YOU DOING
def playlistsave ():
    for file in os.listdir(PLAYLISTPATH):
        if file.endswith('.txt'):
            os.remove(f"{PLAYLISTPATH}/{file}")
    
    for i, playlist in enumerate(playlists):
        name = playlist[0]
        image = playlist[1]
        contents = playlist[2]
        
        reformatted = ""
        for x in contents:
            reformatted += f"{x}\n"
        reformatted = reformatted[:-1]
        
        with open(f"{PLAYLISTPATH}/{i}.txt", "w", encoding="utf-8") as f:
            f.write(f"{name}\n{image}\n{reformatted}")

# create the playlist
def playlistcreate (name, image):
    if not os.path.exists(f"{ICONPATH}/{image}"):
        return 400
    
    playlist = [name, image, []]
    playlists.append(playlist)
    playlistsave()
    return 200

# add a song to ze playlist
def playlistadd (name, song):
    target = None
    for playlist in playlists:
        if playlist[0] == name:
            target = playlist
    
    if target is None: return 400
    if not song in songs: return 400
    
    target[2].append(song)
    playlistsave()
    return 200

# REMOVE a song from the playlist. the song is EVIL.
def playlistremove (name, song):
    target = None
    for playlist in playlists:
        if playlist[0] == name:
            target = playlist
    
    if target is None: return 400
    if song not in target[2]: return 400
    
    target[2].remove(song)
    playlistsave()
    return 200

# BURN IT. BURN IT RIGHT NOW.
def playlistdelete (name):
    for file, playlist in enumerate(playlists):
        if playlist[0] == name:
            playlists.remove(playlist)
            playlistsave()
            return 200
    return 400

def grabmaincolor (image):
    image = img.open(image).convert("RGB")
    extracted = [x / 255 for x in image.resize((1, 1)).getpixel((0, 0))]
    extracted = list(colorsys.rgb_to_hsv(*tuple(extracted)))
    
    s = min(extracted[1] + 0.2, 1)
    if s == 0.2: s = 0
    
    v = max(extracted[2], 0.4)
    v = min(v, 0.8)
    
    h = extracted[0]
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    result = [round(x * 255) for x in [r, g, b]]
    return result

def lengthformat (ms):
    minutes = (ms // 1000) // 60
    seconds = (ms // 1000) - (minutes * 60)
    
    if seconds < 10: seconds = f"0{seconds}"
    
    return f"{minutes}:{seconds}"

def roundpixmap(pixmap, radius):
    result = QtGui.QPixmap(pixmap.size())
    result.fill(QtCore.Qt.transparent)

    painter = QtGui.QPainter(result)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    painter.setClipPath(QtGui.QPainterPath())

    path = QtGui.QPainterPath()
    path.addRoundedRect(result.rect(), radius, radius)

    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    return result

def contentspixmap (pixmap, sizes):
    x1, y1, x2, y2 = tuple(sizes)
    result = QtGui.QPixmap(pixmap).scaled(x1, y1) # this is a placeholder (dont do that please)
    return result

def createplayorder (current):
    global where
    where = 0
    
    usedsongs = []
    for filename, (name, icon) in songs.items():
        usedsongs.append(filename)
    
    if shuffling == True:
        random.shuffle(usedsongs)
    
    result = [current]
    for filename in usedsongs:
        if filename == current: continue
        
        result.append(filename)
    
    if repeating == True:
        result = [current]
    
    return result

# THE GUI BULLSHIT STARTS HERE
class HoverableButton (QtWidgets.QPushButton):
    mouseEnter = QtCore.Signal()
    mouseLeave = QtCore.Signal()
    
    def __init__ (self, normal, hover): # self is FUCKING IMPORTANT DONT YOU FUCKING DARE
        super().__init__() # fyi this part makes "hoverablebutton" into a qpushbutton
        
        self.hovered = False
        
        if normal is not None:
            self.normal = QtGui.QIcon(normal)
            self.setIcon(self.normal)
        else:
            self.normal = None
        if hover is not None:
            self.hover = QtGui.QIcon(hover)
        else:
            self.hover = None
    
    def enterEvent (self, event):
        if self.hover is not None: self.setIcon(self.hover)
        self.hovered = True
        self.mouseEnter.emit() # run the CUSTOM hover signal 
        super().enterEvent(event) # let the button do its usual bullsheit
    
    def leaveEvent (self, event):
        if self.normal is not None: self.setIcon(self.normal)
        self.hovered = False
        self.mouseLeave.emit()
        super().leaveEvent(event) # button has MULTIPLE bullshits so let it LEAVE not enter you fucking idiot

class BetterSlider (QtWidgets.QSlider):
    onrelease = QtCore.Signal()
    
    def __init__ (self, orientation, parent=None):
        super().__init__(orientation, parent) # make it into a slider and specify parent and orientation
        
        self.dragging = False
    
    def mousePressEvent (self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = True
            self.setValue(QtWidgets.QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.position().x(), self.width()))
            event.accept()
            return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event): # no this runs when the mouse is OVER the slider, be jolly 
        if self.dragging:
            self.setSliderPosition(
                QtWidgets.QStyle.sliderValueFromPosition(
                    self.minimum(),
                    self.maximum(),
                    event.position().x(),
                    self.width()
                )
            )
            event.accept()
            return
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False
            self.setSliderPosition(
                QtWidgets.QStyle.sliderValueFromPosition(
                    self.minimum(),
                    self.maximum(),
                    event.position().x(),
                    self.width()
                )
            )
            event.accept()
            self.onrelease.emit()
            return

        super().mouseReleaseEvent(event)

class PlaylistWidgetTemplate (QtWidgets.QPushButton):
    def __init__ (self, name, contents, image=f"{ICONPATH}/placeholder.png", parent=None):
        super().__init__(parent)
        
        self.hlayout = QtWidgets.QHBoxLayout(self)
        self.icon = QtWidgets.QLabel()
        self.icon.setPixmap(roundpixmap(QtGui.QPixmap(image).scaled(50, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation), 4))
        self.icon.setMinimumSize(50, 50)
        self.maincolor = grabmaincolor(image) # the monolith has fallen.
        self.textholder = QtWidgets.QWidget()
        self.textholder.setStyleSheet("background: transparent")
        self.vlayout = QtWidgets.QVBoxLayout(self.textholder)
        self.vlayout.setContentsMargins(0, 5, 0, 15)
        self.duration = QtWidgets.QWidget()
        self.duration.setStyleSheet("background: transparent")
        self.durationlayout = QtWidgets.QHBoxLayout(self.duration)
        self.durationlayout.setContentsMargins(0, 0, 0, 0)
        self.durationtext = QtWidgets.QLabel(f"{len(contents)} songs")
        self.durationtext.setFont(font)
        self.durationtext.setStyleSheet(f"font-style: italic;\ncolor: rgb({round(min(self.maincolor[0] * 1.5, 255))}, {round(min(self.maincolor[1] * 1.5, 255))}, {round(min(self.maincolor[2] * 1.5, 255))});\nfont-size: 12px")
        self.durationtext.setAlignment(QtCore.Qt.AlignLeft)
        self.durationicon = QtWidgets.QLabel()
        self.durationicon.setPixmap(QtGui.QPixmap(f"{ICONPATH}/playlist.png").scaled(15, 15, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.duration.setFixedHeight(14)
        self.durationlayout.addWidget(self.durationicon)
        self.durationlayout.addWidget(self.durationtext, 1)
        self.text = QtWidgets.QLabel(name)
        self.text.setFont(font)
        self.text.setStyleSheet("color: white;\nfont-style: italic;\nfont-weight: 700\n;\nfont-size: 18px")
        self.text.setAlignment(QtCore.Qt.AlignLeft)
        self.vlayout.addWidget(self.text)
        self.vlayout.addWidget(self.duration)
        self.button = QtWidgets.QLabel()
        self.button.setPixmap(QtGui.QPixmap(f"{ICONPATH}/playtriangle.png").scaled(50, 50, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation))
        self.button.setMinimumSize(50, 50)
        self.button.hide()
        self.contents = contents
        self.hlayout.addWidget(self.icon)
        self.hlayout.addWidget(self.textholder, 1)
        self.hlayout.addWidget(self.button)
        self.setStyleSheet(f"""QPushButton {{background: qlineargradient(
        x1: 0, y1: 0,
        x2: 0.5, y2: 0,
        stop: 0 rgb({self.maincolor[0]}, {self.maincolor[1]}, {self.maincolor[2]}),
        stop: 1 #0f0f0f)}}
        QLabel {{background: transparent}}""")
        
    def enterEvent (self, event):
        super().enterEvent(event)
        self.button.show()
    
    def leaveEvent (self, event):
        super().leaveEvent(event)
        self.button.hide()

class SongWidgetTemplate (QtWidgets.QPushButton):
    def __init__ (self, name, filename, image=f"{ICONPATH}/placeholder.png", parent=None):
        super().__init__(parent)
        
        self.hlayout = QtWidgets.QHBoxLayout(self)
        self.icon = QtWidgets.QLabel()
        self.icon.setPixmap(roundpixmap(QtGui.QPixmap(image).scaled(50, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation), 4))
        self.icon.setMinimumSize(50, 50)
        self.maincolor = grabmaincolor(image)
        self.textholder = QtWidgets.QWidget()
        self.textholder.setStyleSheet("background: transparent")
        self.vlayout = QtWidgets.QVBoxLayout(self.textholder)
        self.vlayout.setContentsMargins(0, 5, 0, 15)
        self.duration = QtWidgets.QWidget()
        self.duration.setStyleSheet("background: transparent")
        self.durationlayout = QtWidgets.QHBoxLayout(self.duration)
        self.durationlayout.setContentsMargins(0, 0, 0, 0)
        media = vlc.Media(filename)
        media.parse()
        while media.get_duration() == -1: time.sleep(0.01)
        self.durationtext = QtWidgets.QLabel(lengthformat(media.get_duration()))
        self.durationtext.setFont(font)
        self.durationtext.setStyleSheet(f"font-style: italic;\ncolor: rgb({round(min(self.maincolor[0] * 1.5, 255))}, {round(min(self.maincolor[1] * 1.5, 255))}, {round(min(self.maincolor[2] * 1.5, 255))});\nfont-size: 12px")
        self.durationtext.setAlignment(QtCore.Qt.AlignLeft)
        self.durationicon = QtWidgets.QLabel()
        self.durationicon.setPixmap(QtGui.QPixmap(f"{ICONPATH}/song.png").scaled(15, 15, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.duration.setFixedHeight(14)
        self.durationlayout.addWidget(self.durationicon)
        self.durationlayout.addWidget(self.durationtext, 1)
        self.filename = filename
        self.text = QtWidgets.QLabel(name)
        self.text.setFont(font)
        self.text.setStyleSheet("color: white;\nfont-style: italic;\nfont-weight: 700\n;\nfont-size: 18px")
        self.text.setAlignment(QtCore.Qt.AlignLeft)
        self.vlayout.addWidget(self.text)
        self.vlayout.addWidget(self.duration)
        self.button = QtWidgets.QLabel()
        self.button.setPixmap(QtGui.QPixmap(f"{ICONPATH}/playtriangle.png").scaled(50, 50, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation))
        self.button.setMinimumSize(50, 50)
        self.button.hide()
        self.hlayout.addWidget(self.icon)
        self.hlayout.addWidget(self.textholder, 1)
        self.hlayout.addWidget(self.button)
        self.setStyleSheet(f"""QPushButton {{background: qlineargradient(
        x1: 0, y1: 0,
        x2: 0.5, y2: 0,
        stop: 0 rgb({self.maincolor[0]}, {self.maincolor[1]}, {self.maincolor[2]}),
        stop: 1 #0f0f0f)}}
        QLabel {{background: transparent}}""")
        
    def enterEvent (self, event):
        super().enterEvent(event)
        self.button.show()
    
    def leaveEvent (self, event):
        super().leaveEvent(event)
        self.button.hide()

app = QtWidgets.QApplication([])
window = QtWidgets.QMainWindow()
window.resize(1400, 830)
holder = QtWidgets.QWidget()
holder.setStyleSheet("background-color: black")
window.setCentralWidget(holder)

holderlayout = QtWidgets.QVBoxLayout(holder)
barholder = QtWidgets.QWidget()
barholder.setStyleSheet("border-bottom: 1px solid #2a2a2a")
barholder.setFixedHeight(30)
upperholder = QtWidgets.QWidget()
bottomholder = QtWidgets.QWidget()
holderlayout.addWidget(barholder)
holderlayout.addWidget(upperholder, 9)
holderlayout.addWidget(bottomholder, 1)

upperlayout = QtWidgets.QHBoxLayout(upperholder)
upperlayout.setSpacing(15)
listbox = QtWidgets.QWidget()
listbox.setStyleSheet("""background-color: #0f0f0f;
border-radius: 5px""")
contentsbox = QtWidgets.QWidget()
contentsbox.setStyleSheet("""background-color: #0f0f0f;
border-radius: 5px""")
upperlayout.addWidget(listbox, 1)
upperlayout.addWidget(contentsbox, 3)

controlvlayout = QtWidgets.QVBoxLayout(bottomholder)
controlvlayout.setContentsMargins(0, 0, 0, 0)
controlvlayout.setSpacing(0)
lowcontrolholder = QtWidgets.QWidget()
highcontrolholder = QtWidgets.QWidget()
controlvlayout.addWidget(highcontrolholder, 2)
controlvlayout.addWidget(lowcontrolholder, 1)

hclayout = QtWidgets.QHBoxLayout(highcontrolholder)
hclayout.setAlignment(QtCore.Qt.AlignVCenter)
nextbutton = HoverableButton(f"{ICONPATH}/nextbutton.png", f"{ICONPATH}/nextbuttonhover.png")
nextbutton.setMinimumSize(50, 30)
nextbutton.setIconSize(QtCore.QSize(20, 20))
prevbutton = HoverableButton(f"{ICONPATH}/prevbutton.png", f"{ICONPATH}/prevbuttonhover.png")
prevbutton.setMinimumSize(50, 30)
prevbutton.setIconSize(QtCore.QSize(20, 20))
pausebutton = QtWidgets.QPushButton()
pausebutton.setMinimumSize(40, 40)
pausebutton.setIconSize(QtCore.QSize(40, 40))
pausebutton.setIcon(QtGui.QIcon(f"{ICONPATH}/pausebutton.png"))
shufflebutton = HoverableButton(f"{ICONPATH}/shuffle.png", f"{ICONPATH}/shufflehover.png")
shufflebutton.setMinimumSize(25, 25)
shufflebutton.setIconSize(QtCore.QSize(20, 20))
repeatbutton = HoverableButton(f"{ICONPATH}/repeat.png", f"{ICONPATH}/repeathover.png")
repeatbutton.setMinimumSize(25, 25)
repeatbutton.setIconSize(QtCore.QSize(20, 20))
hcspacing1 = QtWidgets.QWidget()
hcspacing2 = QtWidgets.QWidget()
hclayout.addWidget(hcspacing1, 20)
hclayout.addWidget(shufflebutton, 1)
hclayout.addWidget(prevbutton, 1)
hclayout.addWidget(pausebutton, 1)
hclayout.addWidget(nextbutton, 1)
hclayout.addWidget(repeatbutton, 1)
hclayout.addWidget(hcspacing2, 20)

lclayout = QtWidgets.QHBoxLayout(lowcontrolholder)
lclayout.setContentsMargins(0, 0, 0, 0)
progressholder = QtWidgets.QWidget()
lcspacing1 = QtWidgets.QWidget()
lcspacing2 = QtWidgets.QWidget()
lclayout.addWidget(lcspacing1, 1)
lclayout.addWidget(progressholder, 2)
lclayout.addWidget(lcspacing2, 1)
progresslayout = QtWidgets.QHBoxLayout(progressholder)
progressionslider = BetterSlider(QtCore.Qt.Horizontal)
progressionslider.setRange(0, 1000)
progressionslider.setValue(progress)
progressionslider.setStyleSheet("""QSlider::handle:horizontal {background-color: #ffffff;
width: 6px;
height: 6px;
border-radius: 3px}
QSlider::sub-page:horizontal {background-color: rgb(""" + f"{maincolor[0]}, {maincolor[1]}, {maincolor[2]}" + """);
border-radius: 3px}
QSlider::groove:horizontal {background-color: #3d3d3d;
height: 6px;
border-radius: 3px}""")
progressionslider.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
currenttime = QtWidgets.QLabel("0:00")
currenttime.setStyleSheet("""color: #8d8d8d;
font-weight: 600""")
totaltime = QtWidgets.QLabel("x:xx")
totaltime.setStyleSheet("""color: #8d8d8d;
font-weight: 600""")
currenttime.setAlignment(QtCore.Qt.AlignVCenter)
totaltime.setAlignment(QtCore.Qt.AlignVCenter)
currenttime.setFont(font)
totaltime.setFont(font)
progresslayout.addWidget(currenttime)
progresslayout.addWidget(progressionslider, 1)
progresslayout.addWidget(totaltime)
s2layout = QtWidgets.QHBoxLayout(lcspacing2)
volspacer = QtWidgets.QWidget()
volholder = QtWidgets.QWidget()
s2layout.addWidget(volspacer, 1)
s2layout.addWidget(volholder)
vollayout = QtWidgets.QHBoxLayout(volholder)
volbutton = HoverableButton(None, None)
volbutton.setMinimumSize(15, 15)
volbutton.setIconSize(QtCore.QSize(15, 15))
volslider = BetterSlider(QtCore.Qt.Horizontal)
volslider.setRange(0, 100)
volslider.setValue(volume)
volslider.setStyleSheet("""QSlider::handle:horizontal {background-color: #ffffff;
width: 6px;
height: 6px;
border-radius: 3px}
QSlider::sub-page:horizontal {background-color: rgb(""" + f"{maincolor[0]}, {maincolor[1]}, {maincolor[2]}" + """);
border-radius: 3px}
QSlider::groove:horizontal {background-color: #3d3d3d;
height: 6px;
border-radius: 3px}""")
if volume > 50: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumefull.png"))
if volume < 50: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumehalf.png"))
if volume == 0: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumemuted.png"))
vollayout.addWidget(volbutton, 1)
vollayout.addWidget(volslider)

listboxlayout = QtWidgets.QVBoxLayout(listbox)
listheaderholder = QtWidgets.QWidget()
listheaderholder.setStyleSheet("border-bottom: 1px solid #2a2a2a")
listheaderlayout = QtWidgets.QHBoxLayout(listheaderholder)
listtitle = QtWidgets.QLabel("Music library")
listtitle.setStyleSheet("""font-weight: 800;
color: white;
border: none;
font-size: 16px""")
listtitle.setAlignment(QtCore.Qt.AlignLeft)
listtitle.setFont(font)
addplaylistbutton = HoverableButton(f"{ICONPATH}/addbutton.png", f"{ICONPATH}/addbuttonhover.png")
addplaylistbutton.setStyleSheet("border: none")
addplaylistbutton.setMinimumSize(25, 25)
addplaylistbutton.setIconSize(QtCore.QSize(25, 25))
listheaderlayout.addWidget(listtitle, 1)
listheaderlayout.addWidget(addplaylistbutton)
musiclistarea = QtWidgets.QScrollArea()
musiclistarea.setWidgetResizable(True)
listboxlayout.addWidget(listheaderholder, 1)
listboxlayout.addWidget(musiclistarea, 14)

musiclist = QtWidgets.QWidget()
musiclistlayout = QtWidgets.QVBoxLayout(musiclist)
musiclistlayout.setAlignment(QtCore.Qt.AlignTop)
musiclistlayout.setSpacing(0)
musiclistarea.setWidget(musiclist)

stackholderlayout = QtWidgets.QVBoxLayout(contentsbox)
stackholderlayout.setContentsMargins(0, 0, 0, 0)
contentsstack = QtWidgets.QStackedWidget()
stackholderlayout.addWidget(contentsstack)

singlesongholder = QtWidgets.QWidget()
singlesongholder.setStyleSheet("background: transparent")
contentsstack.addWidget(singlesongholder)
singlevlayout = QtWidgets.QVBoxLayout(singlesongholder)
singlevlayout.setContentsMargins(0, 0, 0, 125)
singleiconholder = QtWidgets.QLabel()
singlename = QtWidgets.QLabel()
singlename.setAlignment(QtCore.Qt.AlignCenter)
singlename.setFont(font)
singlename.setStyleSheet("""color: white;
font-weight: 900;
font-size: 35px""")
singlevlayout.addWidget(singleiconholder, 4)
singlevlayout.addWidget(singlename, 1)

def updatemaincolor ():
    progressionslider.setStyleSheet("""QSlider::handle:horizontal {background-color: #ffffff;
    width: 6px;
    height: 6px;
    border-radius: 3px}
    QSlider::sub-page:horizontal {background-color: rgb(""" + f"{maincolor[0]}, {maincolor[1]}, {maincolor[2]}" + """);
    border-radius: 3px}
    QSlider::groove:horizontal {background-color: #3d3d3d;
    height: 6px;
    border-radius: 3px}""")
    
    volslider.setStyleSheet("""QSlider::handle:horizontal {background-color: #ffffff;
    width: 6px;
    height: 6px;
    border-radius: 3px}
    QSlider::sub-page:horizontal {background-color: rgb(""" + f"{maincolor[0]}, {maincolor[1]}, {maincolor[2]}" + """);
    border-radius: 3px}
    QSlider::groove:horizontal {background-color: #3d3d3d;
    height: 6px;
    border-radius: 3px}""")
updatemaincolor()

def onpausebutton ():
    pause()
    if paused: pausebutton.setIcon(QtGui.QIcon(f"{ICONPATH}/pausebutton1.png"))
    else: pausebutton.setIcon(QtGui.QIcon(f"{ICONPATH}/pausebutton.png"))
pausebutton.clicked.connect(onpausebutton)

def onvolsliderchange ():
    global volume
    volume = volslider.value()
    
    if volume > 50: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumefull.png"))
    if volume < 50: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumehalf.png"))
    if volume == 0: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumemuted.png"))
    
    if player is not None: player.audio_set_volume(volume)
volslider.valueChanged.connect(onvolsliderchange)

def onvolbuttonclick ():
    global volume
    global prevvolume
    
    if volume != 0:
        prevvolume = volume
        volume = 0
        volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumemutedhover.png"))
    else:
        volume = prevvolume
        if volume > 50: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumefullhover.png"))
        if volume < 50: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumehalfhover.png"))
        if volume == 0: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumemutedhover.png"))
    
    volslider.setValue(volume)
volbutton.clicked.connect(onvolbuttonclick)

def onvolbuttonhover ():
    if not volbutton.hovered:
        if volume > 50: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumefull.png"))
        if volume < 50: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumehalf.png"))
        if volume == 0: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumemuted.png"))
    else:
        if volume > 50: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumefullhover.png"))
        if volume < 50: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumehalfhover.png"))
        if volume == 0: volbutton.setIcon(QtGui.QIcon(f"{ICONPATH}/volumemutedhover.png"))
volbutton.mouseEnter.connect(onvolbuttonhover)
volbutton.mouseLeave.connect(onvolbuttonhover)

def onsinglesongpress (button):
    global maincolor
    global playorder
    
    filename = button.filename
    maincolordata = button.maincolor
    
    maincolor = maincolordata
    updatemaincolor()
    
    contentsstack.setCurrentWidget(singlesongholder)
    singlename.setText(songs[filename][0])
    singleiconholder.setPixmap(contentspixmap(f"{ICONPATH}/albumart/{songs[filename][1]}", [singleiconholder.width(), singleiconholder.height(), 100, 100]))
    
    pausebutton.setIcon(QtGui.QIcon(f"{ICONPATH}/pausebutton.png"))
    
    play(filename)
    
    playorder = createplayorder(filename)

def updateprogressslider ():
    if player is None: return
    
    totalduration = player.get_length()
    currentposition = player.get_position()
    currenttimevalue = player.get_time()
    
    currenttime.setText(lengthformat(currenttimevalue))
    totaltime.setText(lengthformat(totalduration))
    
    if progressionslider.dragging == False:
        progressionslider.setValue(currentposition * 1000)
    
progresstimer = QtCore.QTimer()
progresstimer.timeout.connect(updateprogressslider)
progresstimer.start(250)

def onnextsongpress ():
    global where
    global maincolor
    
    if not playorder: return
    
    where += 1
    if where >= len(playorder):
        where = 0
    
    if contentsstack.currentWidget() == singlesongholder:
        song = None
        try: song = songs[playorder[where]] # playorder[where] is a full path btw and if u dont know what does it return im going to eat you
        except KeyError:
            onnextsongpress()
            return
        
        filename = playorder[where]
        maincolordata = grabmaincolor(f"{ICONPATH}/albumart/{song[1]}")
        
        maincolor = maincolordata
        updatemaincolor()
        
        singlename.setText(song[0])
        singleiconholder.setPixmap(contentspixmap(f"{ICONPATH}/albumart/{song[1]}", [singleiconholder.width(), singleiconholder.height(), 100, 100]))
        
        play(filename)
nextbutton.clicked.connect(onnextsongpress)

def onprevsongpress ():
    global where
    global maincolor
    
    if not playorder: return
    
    where -= 1
    if where < 0:
        where = len(playorder) - 1
    
    if contentsstack.currentWidget() == singlesongholder:
        song = None
        try: song = songs[playorder[where]]
        except KeyError:
            onprevsongpress()
            return
        
        filename = playorder[where]
        maincolordata = grabmaincolor(f"{ICONPATH}/albumart/{song[1]}")
        
        maincolor = maincolordata
        updatemaincolor()
        
        singlename.setText(song[0])
        singleiconholder.setPixmap(contentspixmap(f"{ICONPATH}/albumart/{song[1]}", [singleiconholder.width(), singleiconholder.height(), 100, 100]))
        
        play(filename)
prevbutton.clicked.connect(onprevsongpress)

def onshufflepress ():
    global shuffling
    shuffling = not shuffling
    
    if shuffling:
        shufflebutton.normal = QtGui.QIcon(f"{ICONPATH}/shuffleon.png")
        shufflebutton.hover = QtGui.QIcon(f"{ICONPATH}/shuffleon.png")
    else:
        shufflebutton.normal = QtGui.QIcon(f"{ICONPATH}/shuffle.png")
        shufflebutton.hover = QtGui.QIcon(f"{ICONPATH}/shufflehover.png")
    
    shufflebutton.setIcon(shufflebutton.hover)
shufflebutton.clicked.connect(onshufflepress)

def onrepeatpress ():
    global repeating
    global playorder
    repeating = not repeating
    
    if repeating:
        repeatbutton.normal = QtGui.QIcon(f"{ICONPATH}/repeaton.png")
        repeatbutton.hover = QtGui.QIcon(f"{ICONPATH}/repeaton.png")
        
        shuffledsongs = []
        newplayorder = []
        for i, x in enumerate(playorder):
            if i > where:
                shuffledsongs.append(x)
            else:
                newplayorder.append(x)
        random.shuffle(shuffledsongs)
        newplayorder += shuffledsongs
        
        playorder = newplayorder
    else:
        repeatbutton.normal = QtGui.QIcon(f"{ICONPATH}/repeat.png")
        repeatbutton.hover = QtGui.QIcon(f"{ICONPATH}/repeathover.png")
        
        if contentsstack.currentWidget() == singlesongholder:
            playorder = createplayorder(playorder[where])
    repeatbutton.setIcon(repeatbutton.hover)
repeatbutton.clicked.connect(onrepeatpress)

def onprogresschange ():
    if player is None: return
    
    player.set_position(progressionslider.value() / 1000)
progressionslider.onrelease.connect(onprogresschange)

def updatemusiclist ():
    while musiclistlayout.count():
        widget = musiclistlayout.takeAt(0).widget()
        if widget is not None: widget.deleteLater()
    
    for x in playlists:
        name = x[0]
        image = x[1]
        contents = x[2]
        
        widget = PlaylistWidgetTemplate(name=name, image=f"{ICONPATH}/albumart/{image}", contents=contents)
        widget.setFixedHeight(80) # pro tip: just use sharex as a ruler (and win)
        musiclistlayout.addWidget(widget)
    
    if songs and playlists:
        spacer = QtWidgets.QWidget()
        spacer.setFixedHeight(25)
        spacer.setStyleSheet("background: transparent")
        spacerlayout = QtWidgets.QHBoxLayout(spacer)
        bar = QtWidgets.QWidget()
        bar.setFixedHeight(2)
        bar.setStyleSheet("""background: #202020""")
        spacerlayout.addWidget(bar)
        musiclistlayout.addWidget(spacer)
    else: print("uh oh, the files had breached containment")
    
    for filename, (name, icon) in songs.items():
        widget = SongWidgetTemplate(name=name, image=f"{ICONPATH}/albumart/{icon}", filename=filename)
        widget.setFixedHeight(80)
        musiclistlayout.addWidget(widget)
        
        widget.clicked.connect(lambda checked=False, w=widget: onsinglesongpress(w))
updatemusiclist()

window.show()
app.exec()