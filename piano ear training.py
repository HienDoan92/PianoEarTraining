from tkinter import *
import pyaudio
import wave
import random
import sys
import threading
from tkinter import messagebox

class App:
    def __init__(self, root):
        self.screenHeight = root.winfo_height()
        self.screenWidth = root.winfo_width()
        if self.screenHeight < 768:
            self.A0_left = 10
            self.A0_top = 170
            self.pianoKeyRowsStep = 250
            self.pianoKeyRowsOffset = 170

        elif self.screenHeight > 768 and self.screenHeight < 1024:
            self.A0_left = 10
            self.A0_top = 250
            self.pianoKeyRowsStep = 250
            self.pianoKeyRowsOffset = 250

        else:
            pass

        self.frame = Frame(root,bg='#252525')
        self.frame.pack(fill='both', expand='yes')
        menu = Menu(root)
        root.config(menu=menu)
        actionMenu = Menu(menu, tearoff=False)
        menu.add_cascade(label='Action',menu=actionMenu)
        actionMenu.add_command(label='Listen again          ', command=self.listenAgain, accelerator="l")
        actionMenu.add_command(label='Show hint         ', command=self.showHint, accelerator="h")
        helpMenu = Menu(menu, tearoff=False)
        menu.add_cascade(label='Help',menu=helpMenu)
        helpMenu.add_command(label='How to use          ', command=self.showHelp)
        helpMenu.add_command(label='About       ', command=self.showAbout)
        self.bottomStatus = Label(root,bd=1, relief=SUNKEN, anchor=W, bg='#007ACC', fg='white')
        self.bottomStatus.pack(side=BOTTOM, fill=X)
        self.hintLabel = Label(self.frame, fg='#C586C0', bg='#252525',font = "Verdana 30 italic")
        self.hintLabel.place(rely=0.1, relx=0.5, x=0, y=0, anchor=N)
        self.rightLabel = Label(self.frame,bg='#252525',font = "Verdana 24", fg='green')
        self.rightLabel.place(rely=0.0, relx=0.95, x=0, y=0, anchor=NE)
        self.wrongLabel = Label(self.frame,fg='#F30202', bg='#252525',font = "Verdana 24")
        self.wrongLabel.place(rely=0.08, relx=0.95, x=0, y=0, anchor=NE)
        self.notificationLabel = Label(self.frame,fg='#C586C0',bg='#252525',font = "Verdana 30 italic")
        self.notificationLabel.place(rely=0.1, relx=0.5, x=0, y=0, anchor=N)
        self.frame.bind_all("<l>", self.listenAgainFromHotkey)
        self.frame.bind_all("<h>", self.showHintFromHotkey)
                    
        self.blackKeyPosition = [1,4,6,9,11,13,16,18,21,23,25,28,30,33,35,37,40,42,45,47,49,52,54,57,59,61,64,66,69,71,73,76,78,81,83,85]
        self.pianoKeyIndex = 0
        self.octave = 0
        self.whiteKeyPosition = 0
        self.pianoKeyDictionary = {}
        self.isShowedHint = False
        self.streamDict = {}
        self.p = pyaudio.PyAudio()
        self.currentPianoKeyIndex = -1        
        self.right = 0
        self.wrong = 0
        self.firstQuiz = True

        self.drawKeyboard()
        self.drawScoreboard()
        self.showHelp()
        self.generateNextQuiz()

    def drawScoreboard(self):
        self.rightLabel.config(text = 'Right : '+str(self.right))
        self.wrongLabel.config(text = 'Wrong : '+str(self.wrong))
    
    def drawKeyboard(self):
        for i in range(2):   
            if i == 0:
                left = self.A0_left
            else:
                left = self.A0_left + self.pianoKeyRowsOffset

            for j in range(44):
                if self.pianoKeyIndex in self.blackKeyPosition:
                    temp = self.pianoKeyIndex % 6
                    if temp == 0:
                        keyLabel = 'D#'+str(self.octave)
                    elif temp == 1:
                        keyLabel = 'A#'+str(self.octave)
                    elif temp == 3:
                        keyLabel = 'F#'+str(self.octave)
                    elif temp == 4:
                        keyLabel = 'C#'+str(self.octave)
                    elif temp == 5:
                        keyLabel = 'G#'+str(self.octave)
                    else:
                        pass
                    b = Button(self.frame, width="3", bg='black',height="8",activebackground="#808080",command=lambda i=self.pianoKeyIndex:self.pianoKeyPress(i))
                    b.place(x=left,y=self.A0_top)            
                    b.lift()
                    b.bind('<Enter>', lambda event, butt=b: butt.config(bg='#569CD6'))
                    b.bind('<Leave>', lambda event, butt=b: butt.config(bg='black'))
                else:
                    temp = self.whiteKeyPosition % 7
                    if temp == 0:
                        keyLabel = 'A'+str(self.octave)
                    elif temp == 1:
                        keyLabel = 'B'+str(self.octave)
                    elif temp == 2:
                        self.octave += 1
                        keyLabel = 'C'+str(self.octave)    
                    elif temp == 3:
                        keyLabel = 'D'+str(self.octave) 
                    elif temp == 4:
                        keyLabel = 'E'+str(self.octave) 
                    elif temp == 5:
                        keyLabel = 'F'+str(self.octave) 
                    elif temp == 6:
                        keyLabel = 'G'+str(self.octave)
                    else:
                        pass
                    
                    b = Button(self.frame, width="5", bg='white',height="14",text=keyLabel,anchor='s',command=lambda i=self.pianoKeyIndex:self.pianoKeyPress(i))
                    b.place(x=left,y=self.A0_top)
                    b.lower()
                    b.bind('<Enter>', lambda event, butt=b: butt.config(bg='#569CD6'))
                    b.bind('<Leave>', lambda event, butt=b: butt.config(bg='white'))
                    self.whiteKeyPosition += 1

                self.pianoKeyDictionary[str(self.pianoKeyIndex)] = keyLabel
                if (self.pianoKeyIndex+1 in self.blackKeyPosition) and (self.pianoKeyIndex not in self.blackKeyPosition):
                    left += 30
                elif (self.pianoKeyIndex+1 not in self.blackKeyPosition) and (self.pianoKeyIndex not in self.blackKeyPosition):
                    left += 45
                elif (self.pianoKeyIndex+1 not in self.blackKeyPosition) and (self.pianoKeyIndex in self.blackKeyPosition):
                    left += 15

                self.pianoKeyIndex += 1
            self.A0_top += self.pianoKeyRowsStep

    def showHelp(self):
        m = 'Listen to the playing note, then try to press corresponding key on the piano.'
        m += '\n\n'
        m+= '- Press hotkey \"l\" to listen to the note again.'
        m+= '\n'
        m+= '- Press hotkey \"h\" to get hint.'
        messagebox.showinfo("How to use", m)

    def showAbout(self):
        m = 'Version : 1.0'
        m+= '\n\n'
        m+= 'Date release : Jan 20, 2017'
        m+= '\n\n'
        m+= 'Author : doanhien4392@gmail.com'
        messagebox.showinfo("Simple ear training", m)
    
    def setNotificationText(self,t):
        self.notificationLabel.config(text=t)

    def generateNextQuiz(self):            
        self.currentPianoKeyIndex = random.randrange(15, 75)
        # print(currentPianoKeyIndex)
        self.isShowedHint = False
        self.hintLabel.config(text='')
        if self.firstQuiz == False:
            self.notificationLabel.config(text=' --- Next quiz ---')
        self.playSound(self.currentPianoKeyIndex)
        self.firstQuiz = False
        threading.Timer(2, self.setNotificationText,['']).start()

    def pianoKeyPress(self, i):
        self.bottomStatus.config(text=' You just pressed '+self.pianoKeyDictionary[str(i)])
        self.playSound(i)
        if i == self.currentPianoKeyIndex:
            # correct
            self.right += 1
            self.rightLabel.config(text = 'Right : '+str(self.right))
            self.hintLabel.config(text='')
            self.notificationLabel.config(text = '--- '+self.pianoKeyDictionary[str(i)]+' is correct ---')
            threading.Timer(2, self.generateNextQuiz).start()
        elif i < self.currentPianoKeyIndex:
            self.wrong += 1
            self.wrongLabel.config(text = 'Wrong : '+str(self.wrong))
            if self.isShowedHint == False:
                self.hintLabel.config(text='Higher')
                threading.Timer(1, self.setNotificationText,['']).start()
        else:
            self.wrong += 1
            self.wrongLabel.config(text = 'Wrong : '+str(self.wrong))
            if self.isShowedHint == False:
                self.hintLabel.config(text='Lower')
                threading.Timer(1, self.setNotificationText,['']).start()

    def showHint(self):  
        if self.isShowedHint == False:
            self.isShowedHint = True
            temp = random.randrange(3)
            if temp == 0:
                hint = 'From '+ self.pianoKeyDictionary[str(self.currentPianoKeyIndex - 2)] + ' to ' + self.pianoKeyDictionary[str(self.currentPianoKeyIndex)]
            elif temp == 1:
                hint = 'From '+ self.pianoKeyDictionary[str(self.currentPianoKeyIndex - 1)] + ' to ' + self.pianoKeyDictionary[str(self.currentPianoKeyIndex + 1)]
            else:
                hint = 'From '+ self.pianoKeyDictionary[str(self.currentPianoKeyIndex)] + ' to ' + self.pianoKeyDictionary[str(self.currentPianoKeyIndex + 2)]        
            self.hintLabel.config(text=hint)

    def listenAgain(self):
        self.playSound(self.currentPianoKeyIndex)

    def listenAgainFromHotkey(self, event):
        self.playSound(self.currentPianoKeyIndex)

    def showHintFromHotkey(self, event):
        self.showHint()

    def playSound(self, index):
        if str(self.pianoKeyIndex) in self.streamDict:
            self.streamDict[str(self.pianoKeyIndex)].stop_stream()
            del self.streamDict[str(self.pianoKeyIndex)]
        filename = str(index)+'.wav'
        f = wave.open('notes\\'+filename,"rb")
        def streamCallback(in_data, frame_count, time_info, status):
            data = f.readframes(frame_count)
            return (data, pyaudio.paContinue)    
        stream = self.p.open(format=self.p.get_format_from_width(f.getsampwidth()), channels=f.getnchannels(), rate=f.getframerate(), output=True, stream_callback=streamCallback)    
        self.streamDict[str(self.pianoKeyIndex)] = stream
        stream.start_stream()

if __name__ == "__main__":
    root = Tk()
    root.state("zoomed")
    root.title('Simple ear training')
    root.iconbitmap('icon.ico')
    App(root)
    root.mainloop()