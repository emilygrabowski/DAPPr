# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 14:50:45 2017

@author: emilygrabowski
"""
from atlasutilities import load_praat_default
from automateatlas_ave import automate
import tkinter
from tkinter import ttk
from sklearn.preprocessing import StandardScaler  
from sklearn.neural_network import MLPClassifier

#import sklearn.neighbors.typedefs
from tkinter import filedialog
import os.path
from time import sleep
from tkinter import messagebox
import platform

import os
import sys
if platform.system() == "Darwin":
    file_sep="/"
elif platform.system()=="Windows":
    file_sep="\\"


if getattr(sys, 'frozen',False):
    dname = os.path.dirname(sys.executable)
elif __file__:
    dname = os.path.dirname(os.path.abspath(__file__))
print(dname)
DEFAULT_BG = 'gray90'

class Content(tkinter.Frame):
    """Top Level frame in the GUI"""
    def __init__(self, root):
        tkinter.Frame.__init__(self, root, bg=DEFAULT_BG)
        submit_button = tkinter.Button(self,
                                       command=self.submit_form,
                                       text="Run!",
                                       highlightbackground=DEFAULT_BG)

        self.grid()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=2)
        self.columnconfigure(3, weight=1)

        self.rowconfigure(1, weight=1)

        self.sound = audio_frame(self)
        self.options = options_frame(self)
            #self.output = output_frame(self)
        self.paths = paths_frame(self)


        submit_button.grid(column=3, row=2, sticky=('s'))


    def get_args(self):
        """Get the arguments from the form"""
        warnings = []

        if len(warnings) == 0:
            args = []
            ##get the values from the sound frame##
            args.append(self.sound.audio_file.get())
            #arglist: (audiofile, textfile, outputfile, binvar, und, dh,
            #praat, speakerid, outputid, sylout, elanout, excelout, metaout)
            args.append(self.sound.text_file.get())
            args.append(self.sound.output_file.get())

            ##get the options##
            args.append(self.options.binvar.get())
            args.append(self.options.range.get())
            args.append('empty')

            ##get the paths##
            args.append(self.paths.praat_path.get())
            args.append(self.paths.speaker_id.get())
            args.append(self.paths.output_id.get())

            ##output options##
#            args.append(self.output.sylout.get())
#            args.append(self.output.elanout.get())
#            args.append(self.output.excelout.get())
#            args.append(self.output.metaout.get())
            args.append(self.options.tritone.get())
            args.append(self.paths.prevsp.get())
            args.append(self.options.custom_low.get())
            args.append(self.options.custom_high.get())
            return args

    def submit_form(self):
        """Submit the form"""
        #self.paths.set_speaker()
        #if self.validate_form():
        if True:
            arglist = self.get_args()
            automate(arglist)
        

    def validate_form(self):
        """Validate the input"""
        #if self.paths.check_files():
        return(True)

        

class paths_frame(tkinter.Frame):
    """Frame for the paths input"""

    def __init__(self, content):
        tkinter.Frame.__init__(self, content,
                               relief='groove',
                               bg=DEFAULT_BG,
                               border=5)
        self.grid(column=0, row=2, sticky='nwes')
        self.columnconfigure(1, weight=3)

        ##PRAAT PATH##
        pathlbl = ttk.Label(self, text="Praat Path", background=DEFAULT_BG)
        self.praat_path = tkinter.StringVar()
        self.praat_path.set(load_praat_default())
        praat_entry = ttk.Entry(self, textvariable=self.praat_path,
                               background=DEFAULT_BG)

        ##NEW SPEAKER ID## 
        speakerlbl = ttk.Label(self, text="New Speaker",
                               background=DEFAULT_BG)

        self.speaker_id = tkinter.StringVar()
        self.speaker_id.set("")
        speaker_entry = ttk.Entry(self, textvariable=self.speaker_id,
                                 background=DEFAULT_BG)

        ##PREVIOUS SPEAKER ID##
        prevspeakerlbl = ttk.Label(self, text="Speaker from database",
                                   background = DEFAULT_BG)

        #Get a list of options
        
        spath = os.path.join(dname,'Data')
        slist = os.listdir(spath)+["None"]
        sdefault = "None"

        nslist = [sdefault]
        for i in range(len(slist)):
            if not slist[i][0]=='.':
                nslist.append(slist[i].split()[0].strip())
            
        OPTIONS = nslist
        self.prevsp = tkinter.StringVar(self)
        self.prevsp.set(OPTIONS[0])
        prevspbox = ttk.OptionMenu(self, self.prevsp,*OPTIONS)
#        
#        ##OUTPUT ID##
        outputlbl = ttk.Label(self, text="Output ID",
                              background=DEFAULT_BG)

        self.output_id = tkinter.StringVar()
        self.output_id.set("ejg_5")

        output_entry = ttk.Entry(self, textvariable=self.output_id,
                                background=DEFAULT_BG)


        ##GRID##
        pathlbl.grid(column=0, row=2, sticky=('w'))
        praat_entry.grid(column=1, row=2, sticky=('w'))
        speakerlbl.grid(column=0, row=1, sticky=('w'))
        speaker_entry.grid(column=1, row=1, sticky=('w'))
        #outputlbl.grid(column=0, row=2, sticky=('w'))
        #output_entry.grid(column=1, row=2, sticky='w')
        prevspeakerlbl.grid(column=0, row = 0, sticky = 'w')
        prevspbox.grid(column=1, row=0, sticky='wE')
        
    def check_files(self):
        if not os.path.isfile(self.praat_path.get()):
            if platform.system() == "Darwin":
                self.praat_path.set("/Applications/Praat.app/Contents/MacOS/Praat")
            elif platform.system() == "Windows":
                self.praat_path.set(r"C:\Praat.exe")
            if not os.path.isfile(self.praat_path.get()):
                messagebox.showinfo("Error: Praat Not Found", "The Praat path is not valid. Please check your path and try again")
                return False
            else:
                return True
        else:
            return True
                
    def set_speaker(self):
        print(self.speaker_id.get())
        print(self.prevsp.get())
        ps = self.prevsp.get()
        ns = self.speaker_id.get()
        if ps != "Select a Speaker":
            print('Previous speaker selected')
            speaker = ps
            print(os.listdir(os.path.join(dname,'Data')))
        else:
            if ns == '':
                print('No speaker selected. Proceeding without speaker saving')
            else: 
                speaker = ns
        print('triggered')


class audio_frame(tkinter.Frame):
    """Frame for audio input"""
    def __init__(self, content):
        tkinter.Frame.__init__(self, content,
                               relief='groove',
                               bg=DEFAULT_BG,
                               border=5)

        self.grid(column=0, row=0, sticky='nwe', columnspan=4)
        self.columnconfigure(1, weight=2)

        ###AUDIO INPUT####
        #file#
        audiolbl = ttk.Label(self, text=".wav File/Dir", background=DEFAULT_BG)
        self.audio_file = tkinter.StringVar()
        self.audio_file.set("/Users/emilygrabowski/Desktop/OneDrive/Seenku_analysis_paper/Data/5/")
        self.audio = ttk.Entry(self, textvariable=self.audio_file,
                               width=30, background=DEFAULT_BG)

        audio_browse_button = tkinter.Button(self, command=self.get_audio,
                                             text="Browse...",
                                             highlightbackground=DEFAULT_BG)
        check_button = tkinter.Button(self, command=self.check_files,
                                      text="Check",
                                      highlightbackground=DEFAULT_BG)

        audiolbl.grid(column=0, row=0, sticky=('w'))
        self.audio.grid(column=1, row=0)
        audio_browse_button.grid(column=2, row=0)
        #check_button.grid(column=3, row=2)


        ###TEXT INPUT###
        txtlbl = ttk.Label(self, text=".TextGrid File/Dir",
                           background=DEFAULT_BG)
        self.text_file = tkinter.StringVar()
        self.text_file.set("/Users/emilygrabowski/Desktop/OneDrive/Seenku_analysis_paper/Data/5/")
        text = ttk.Entry(self, textvariable=self.text_file,
                         width=30, background=DEFAULT_BG)
        text_browse_button = tkinter.Button(self, command=self.get_tg,
                                    text="Browse...",
                                    highlightbackground=DEFAULT_BG)

        txtlbl.grid(column=0, row=1, sticky=('w'))
        text.grid(column=1, row=1)
        text_browse_button.grid(column=2, row=1)


        ###OUTPUT####
        outputlbl = ttk.Label(self, text="Output Dir",
                              background=DEFAULT_BG)
        self.output_file = tkinter.StringVar()
        self.output_file.set('')
        out = ttk.Entry(self, textvariable=self.output_file,
                        width=30, background=DEFAULT_BG)
        output_browse_button = tkinter.Button(self, command=self.get_out,
                                              text="Browse...",
                                              highlightbackground=DEFAULT_BG)

        outputlbl.grid(column=0, row=2, sticky=('wns'))
        out.grid(column=1, row=2)
        output_browse_button.grid(column=2, row=2)


    def get_audio(self):
        audio_in = filedialog.askopenfilename()
        self.audio_file.set(audio_in)
    #textIn = filedialog.askopenfilename()

    def get_tg(self):
        text_in = filedialog.askopenfilename()
        self.text_file.set(text_in)

    def get_out(self):
        out_in = filedialog.askdirectory()
        self.output_file.set(out_in)

    def check_files(self):
        warninglist = []
        sleep(2)

        audio_in = self.audio_file.get()
        tg_in = self.text_file.get()
        out_in = self.output_file.get()
        if audio_in[-4:] == ".wav" or audio_in[-4:] == ".WAV":
            if os.path.isfile(audio_in):
                wave_file = True
            else:
                wave_file = False
                warninglist.append("Error: .wav File does not exist")
        else:
            wave_file = False
            warninglist.append("Error: audio file does not have .wav or .WAV extension")
        if self.text_file.get()[-9:] == ".TextGrid":
            tg = True
        else:
            tg = False
            warninglist.append("Error: file does not have .TextGrid extension")
        if tg_in[:-9] == audio_in[:-4]:
            name_match = True
        else:
            name_match = False
            warninglist.append("Warning: Names of .wav and .TextGrid files do not match")
        if os.path.isdir(out_in):
            out_exists = True
        else:
            out_exists = False
            warninglist.append("Error: Output directory does not exist")
        if wave_file and tg and name_match and out_exists:
            warninglist = []
            warninglist.append("Files exist and input .wav and .TextGrid files have matching names.")
            warninglist.append("Output directory exists")
            return True

        return False


class options_frame(tkinter.Frame):
    def __init__(self, content):
        tkinter.Frame.__init__(self, content,
                               bg=DEFAULT_BG, border=5,
                               relief='groove')

        self.grid(column=0, row=1, columnspan=4, sticky='nwe')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
    

        ##NUMBER OF BINS##
        self.binvar = tkinter.IntVar()
        binNumber = tkinter.Scale(self, from_=20, to=1,
                                  label="Bins",
                                  variable=self.binvar,
                                  background=DEFAULT_BG)
        binNumber.set(8)

        ##DIFFERENT UNDEFINED TREATMENT##
        self.range = tkinter.StringVar()
        undlbl = tkinter.Label(self, text="Pitch range",
                               background=DEFAULT_BG)
        

        rangeFemale = tkinter.Radiobutton(self,
                                        text='Female',
                                        variable=self.range,
                                        value='f',
                                        background=DEFAULT_BG)    

        rangeMale = tkinter.Radiobutton(self,
                            text='Male',
                            variable=self.range,
                            value='m',
                            background=DEFAULT_BG)    

        rangeCustom=tkinter.Radiobutton(self,
                            text='Custom',
                            variable=self.range,
                            value='c',
                            background=DEFAULT_BG)    

#
#        undRemove = tkinter.Radiobutton(self,
#                                        text='Remove',
#                                        variable=self.und,
#                                        value='remove',
#                                        background=DEFAULT_BG)
#
#        undIgnore = tkinter.Radiobutton(self,
#                                        text='Ignore',
#                                        variable=self.und,
#                                        value='ignore',
#                                        background=DEFAULT_BG)

        rangeCustom.select()

        ##Doubling-halving analysis##
        self.custom_low = tkinter.StringVar()
        self.custom_high = tkinter.StringVar()

        custom_low_lab = tkinter.Label(self,
                              text="Custom low",
                              background=DEFAULT_BG)
        custom_high_lab= tkinter.Label(self,
                              text="Custom high",
                              background=DEFAULT_BG)
        self.custom_low.set(75)
        self.custom_high.set(500)

        custom_low = ttk.Entry(self, textvariable=self.custom_low,
                         background=DEFAULT_BG)
        custom_high = ttk.Entry(self, textvariable=self.custom_high,
                         background=DEFAULT_BG)
#        dhIgnore = tkinter.Radiobutton(self,
#                                       text='Ignore',
#                                       variable=self.dh,
#                                       value='ignore',
#                                       background=DEFAULT_BG)

#        dhAuto = tkinter.Radiobutton(self,
#                                     text='Automatically Remove',
#                                     variable=self.dh,
#                                     value='auto',
#                                     background=DEFAULT_BG)

#        dhManual = tkinter.Radiobutton(self,
#                                       text='Manually Validate',
#                                       variable=self.dh,
#                                       value='manual',
#                                       background=DEFAULT_BG)
        
        ##Tritones##
        self.tritone = tkinter.StringVar()

        samplelbl = tkinter.Label(self,
                              text="Samples per Token",
                              background=DEFAULT_BG)

        sample_number = tkinter.Scale(self, from_=3, to=2,
                                  variable=self.tritone,
                                  background=DEFAULT_BG)
        sample_number.set(2)
        
        outputLbl = ttk.Label(self, text="Options",
                              background=DEFAULT_BG)
        outputLbl.grid(sticky=('n', 'w'))
        binNumber.grid(column=0, row=1, rowspan=4, sticky=('ns', 'w'))
        rangeMale.grid(column=1, row=2, sticky='nw')
        rangeFemale.grid(column=1, row=3, sticky='nw')
        rangeCustom.grid(column=1, row=1, sticky='nw')
        undlbl.grid(column=1, row=0, sticky='nw')
        custom_low_lab.grid(column=2, row=0, sticky='nw')
        custom_low.grid(column=2, row=1, sticky='nw')
        custom_high_lab.grid(column=2, row=2, sticky='nw')
        custom_high.grid(column=2, row=3, sticky='nw')
        #dhManual.grid(column=2, row=2, sticky='nw')
        #dhIgnore.grid(column=2, row=1, sticky='nw')
        samplelbl.grid(column=3, row=0, sticky='nw')
        sample_number.grid(column=3, row=1, rowspan=3)
        

class output_frame(tkinter.Frame):
    def __init__(self, content):
        tkinter.Frame.__init__(self, content,
                               border=5, relief='groove',
                               bg=DEFAULT_BG)

        outputLbl = ttk.Label(self,
                              text="Types of Output",
                              background=DEFAULT_BG)
        outputLbl.grid()

        #self.grid(column=2, row=2, rowspan=2)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.metaout = tkinter.StringVar()
        mOut = tkinter.Checkbutton(self, text='Metadata',
                                   variable=self.metaout,
                                   onvalue=True, offvalue=False,
                                   background=DEFAULT_BG)
        #mOut.grid(sticky=("w"))
        self.sylout = tkinter.StringVar()
        kOut = tkinter.Checkbutton(self, text='Coarse',
                                   variable=self.sylout,
                                   onvalue=True, offvalue=False,
                                   background=DEFAULT_BG)
        #kOut.grid(sticky=("w"))
        self.excelout = tkinter.StringVar()
        cOut = tkinter.Checkbutton(self, text='Detailed',
                                   variable=self.excelout,
                                   onvalue=True, offvalue=False,
                                   background=DEFAULT_BG)
        #cOut.grid(sticky=("w"))
        self.elanout = tkinter.StringVar()
        dOut = tkinter.Checkbutton(self, text='ELAN-Compatible',
                                   variable=self.elanout,
                                   onvalue=True, offvalue=False,
                                   background=DEFAULT_BG)
        #dOut.grid(sticky=("w"))

        mOut.select()
        kOut.select()
        cOut.select()
        dOut.select()



def gui_implement():
    root = tkinter.Tk()
    root.title("Pitch Analysis")
    #style = ttk.Style()
    #print(style.theme_names())

    #defaultbg = 'gray90'
    #print(defaultbg)
    content = Content(root)
    for child in content.winfo_children():
        child.grid_configure(padx=5, pady=5)
    root.mainloop()

gui_implement()
