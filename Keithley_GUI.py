# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:08:33 2020

@author: ygao
"""

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import matplotlib.pyplot as plt
import sys
import glob
import pandas as pd
import numpy as np
from os.path import basename
import csv
from time import sleep
import time
import datetime
import re
import threading
import queue



re_datetime  = re.compile("^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (2[0-3]|[01][0-9]):[0-5][0-9]:[0-5][0-9]$")
re_timestamp = re.compile("^([0-9]{1,4}):[0-5][0-9]:[0-5][0-9]$")

re_float     = re.compile("^[ ]*[+|-]?\d+([.]\d{1,3})?[ ]*$")
re_int       = re.compile("^[ ]*[+|-]?\d+[ ]*$")


class Keithley_gui():
    def __init__(self, parent):
        self.parent = parent
        self.parent.title('Keithley')
        self.thread_queue = queue.Queue()
        
        self.filenames = []
        self.Mpps = []
        self.mpp = 0
        self.zeit = 0
        
    
    def gui_connect(self):
        availablePorts = self.serial_ports()
        availableBaud  = [ '1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200']
        
        frame_connect = tk.LabelFrame(master=self.parent, text = "connect settings")
        frame_connect.pack(side='top', fill='x') # port baud
    

        self.connect_button = tk.Button(master=frame_connect, text = "Connect", width = 10, command = self.action_connect)
        self.connect_button.pack(side='left', padx='5', pady='5')
        #connect.config(state="normal")

        self.disconnect_button = tk.Button(master=frame_connect, text = "Disconnect", width = 10, command = self.action_disconnect)
        self.disconnect_button.pack(side='left', padx='5', pady='5')
        #disconnect.config(state="disable")
        
        port_label = tk.Label(master=frame_connect, text = "Port")
        port_label.pack(side='left', padx='5', pady='5')

        self.port_box = ttk.Combobox(master=frame_connect, values=availablePorts)
        self.port_box.pack(side='left', padx='5', pady='5')
        
        if availablePorts:
            try:
                self.port_box.current(3)             # <--- preselect port
            except:
                try:
                    self.port_box.current(0)
                except:
                    pass
     

        self.port_box_refresh_button = tk.Button(master=frame_connect, text = "Refresh", width = 10, command = self.action_refresh)
        self.port_box_refresh_button.pack(side='left', padx='5', pady='5')
        
        baud = tk.Label(master=frame_connect, text = "Baud")
        baud.pack(side='left', padx='5', pady='5')

        self.baud_box = ttk.Combobox(master=frame_connect, values=availableBaud)
        self.baud_box.pack(side='left', padx='5', pady='5')
        try:
            self.baud_box.current(7)             # <--- preselect baud
        except:
            pass
    


        self.quitgui_button = tk.Button(master=frame_connect, text = "Exit", width = 10, command=self.action_quitgui)
        self.quitgui_button.pack(side='right', padx='5', pady='5')
    
    
    

    def serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            #ports = glob.glob('/dev/tty[A-Za-z]*')
            ports = glob.glob('/dev/ttyUSB*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')   
    
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
    
        return result  # returns a list of ports
    
    
    def action_connect(self):
        port = self.port_box.get()
        baud = self.baud_box.get()
        
     
        try:
            self.serial_object = serial.Serial(port=str(port),
                                          baudrate=baud,
                                          bytesize=8,
                                          parity='N',
                                          stopbits=1,
                                          timeout=2, # None
                                          xonxoff=False,
                                          rtscts=False,
                                          dsrdtr=False)
            
            self.messaging(self.serial_object, cli=True, gui=True)
            self.able_buttons("connect")
            
        except ValueError:
            print(self.serial_object)
            #action_flush_buffer()
            return
    
    
    def action_disconnect(self):
        try:
            self.serial_object.close()
            self.messaging(self.serial_object, cli=True, gui=True)
            self.able_buttons("disconnect")
        
        except AttributeError:
            print("Closed without Using it -_-")
    
    
    
    def action_refresh(self):
        self.availablePorts = self.serial_ports()
        self.port_box.config(values=self.availablePorts)
        self.port_box.set('')
        try:
           self.port_box.current(0)
        except:
           pass

    
    
    def action_quitgui(self):
        try:
            if self.serial_object:
                if self.serial_object.is_open:
                    self.serial_object.close()
            pass
        except:
            print("serial object did't exist")
            pass
        
        self.parent.destroy()
    

    def button_click():
        pass



    def able_buttons(self, state="connect"):
        if state == "connect":
            self.connect_button.config(state="disable")
            self.disconnect_button.config(state="normal")
            self.port_box_refresh_button.config(state="disable")
            self.quitgui_button.config(state="normal")
            self.disconnect_button.config(state="normal")
            self.send_button.config(state="normal")
            self.clear_button.config(state="normal")
            self.smartsweepbestaetigen_Button.config(state="normal")
            self.starttimer_button.config(state="normal")
            self.send_button.config(state="normal")
    
    
    
    
            
        if state == "disconnect":

            self.connect_button.config(state="normal")
            self.port_box_refresh_button.config(state="normal")
            self.disconnect_button.config(state="disable")
            self.quitgui_button.config(state="normal")
            self.smartsweepbestaetigen_Button.config(state="disable")
            self.starttimer_button.config(state="disable")
            self.send_button.config(state="disable")
            
            
    def gui_globalsettings(self):
        
        frame_globalsettings  = tk.LabelFrame(self.parent, text = "global settings", bd = 3, relief = 'groove')
        frame_globalsettings.pack(side='top', fill='x')  # Scan send ON OFF    
            #scan und send -  frame_1

        self.send_button = tk.Button(master=frame_globalsettings, text = "send", state="disable",width = 10, command = self.action_send)
        self.send_button.pack(side='left', padx='5', pady='5')

        self.data_entry = tk.Entry(master=frame_globalsettings)
        self.data_entry.pack(side='left', padx='5', pady='5')
        self.data_entry.insert(0, "*idn?")





    def action_send(self):
        send_data = str(self.data_entry.get())
        if not send_data:
          self.messaging("no message entry", cli=True, msgbox=True)
        else:
          #self.serial_object.write(send_data.encode('UTF-8'))
          received_data = self.writereadbytes_messiging(send_data)
          print(received_data)
          self.messaging(" > ".join(received_data), cli=True, gui=True)



    def messaging(self, msg="no message", cli=False, gui=False, logfile=False, measfile=False, ivfile=False, msgbox=False):
        if cli:
            print(str(msg))
        if gui:
            self.listbox_listbox.insert(tk.END, str(msg))
            self.listbox_listbox.see(tk.END)
    
    #    if measfile:
    #        filename = measfilename_entry.get()
    #        with open(filename, 'a') as the_file:
    #            the_file.write(msg + '\n')
        if msgbox:
            messagebox.showinfo(title="TDK Lambda GUI", message=msg)



    def writereadbytes(self, in_string):
        #print(">>" + input_string + " wurde eingeschrieben.")
        write_string = in_string + "\r\n"
        self.serial_object.write(write_string.encode("ascii"))
        sleep(0.1)
        #print('[write_read()] Bytes im Buffer: ' + str(self.port_k_objekt.in_waiting))  #Get the number of bytes in the input buffer
        if self.serial_object.in_waiting:
            #print("Input_buffer ist nicht leer!")
            read_string = self.serial_object.readline().decode("utf-8").replace('\n', '').replace('\r', '')
            #print(read_string)
            return str(read_string)
    
        return "no Data"


    def writereadbytesall(self, input_string):
        read_string=[]
        print(">> " + input_string)
        write_string = input_string + "\r\n"
        self.serial_object.write(write_string.encode("ascii"))
        sleep(1)
        #print('[write_readall()] Bytes im Buffer: ' + str(self.port_k_objekt.in_waiting))  #Get the number of bytes in the input buffer
        
        if self.serial_object.in_waiting:
            #print("Input_buffer ist nicht leer!")
            read_string= self.serial_object.readall().decode('utf-8')
            sleep(4)
            return str(read_string)
            
        return "no Data"



    def writereadbytes_messiging(self, in_string):
        timestamp = str(datetime.datetime.now()).split('.')[0] 
    
        # sending
        self.serial_object.write((in_string + '\r\n').encode('UTF-8'))
        sleep(0.1)
    
        # listening
        out_string = ''
        while (self.serial_object.in_waiting):
            out_string = out_string + self.serial_object.readline().decode().replace('\n', '').replace('\r', '')
            sleep(0.01)
        
        return [timestamp, str(in_string), str(out_string)]




    def gui_manual(self):
        frame_manual = tk.LabelFrame(self.parent, text = "sweep settings", bd = 3, relief = 'groove')
        frame_manual.pack(side='top', fill='x')  # filenames
     
        
        # sub_frame frame_sweepconfig
        frame_sweepconfig1 = tk.Frame(master=frame_manual)
        frame_sweepconfig1.pack(side='top', fill='x') # smart sweepi config    
    
    
    
        smartsweepvoltagerange_label = tk.Label(master=frame_sweepconfig1, text = "Vmax [V]")
        smartsweepvoltagerange_label.pack(side='left', padx='5', pady='5')
    
        self.smartsweepvoltagerange_entry = tk.Entry(master=frame_sweepconfig1, width=6)
        self.smartsweepvoltagerange_entry.pack(side='left', padx='5', pady='5')
        self.smartsweepvoltagerange_entry.insert(0, "40")
    
        smartsweepcurrentrange_label = tk.Label(master=frame_sweepconfig1, text = "Imax [A]")
        smartsweepcurrentrange_label.pack(side='left', padx='5', pady='5')
    
        self.smartsweepcurrentrange_entry = tk.Entry(master=frame_sweepconfig1, width=6)
        self.smartsweepcurrentrange_entry.pack(side='left', padx='5', pady='5')
        self.smartsweepcurrentrange_entry.insert(0, "5")
    
    
        smartsweepcurrentlimit_label = tk.Label(master=frame_sweepconfig1, text = "I_limit [A]")
        smartsweepcurrentlimit_label.pack(side='left', padx='5', pady='5')
    
        self.smartsweepcurrentlimit_entry = tk.Entry(master=frame_sweepconfig1, width=6)
        self.smartsweepcurrentlimit_entry.pack(side='left', padx='5', pady='5')
        self.smartsweepcurrentlimit_entry.insert(0, "5")
    
    
        smartsweepshortcircutcurrent_label = tk.Label(master=frame_sweepconfig1, text = "Isc [A]")
        smartsweepshortcircutcurrent_label.pack(side='left', padx='5', pady='5')
    
        self.smartsweepshortcircutcurrent_entry = tk.Entry(master=frame_sweepconfig1, width=6)
        self.smartsweepshortcircutcurrent_entry.pack(side='left', padx='5', pady='5')
        self.smartsweepshortcircutcurrent_entry.insert(0, "9")
    
    
    
    
    
        frame_sweepconfig2 = tk.Frame(master=frame_manual)
        frame_sweepconfig2.pack(side='top', fill='x') # smart sweepi config  
    
    
    
        smartsweepvotagestart_label = tk.Label(master=frame_sweepconfig2, text = "Vstart [V]")
        smartsweepvotagestart_label.pack(side='left', padx='5', pady='5')
    
        self.smartsweepvotagestart_entry = tk.Entry(master=frame_sweepconfig2, width=6)
        self.smartsweepvotagestart_entry.pack(side='left', padx='5', pady='5')
        self.smartsweepvotagestart_entry.insert(0, "0")
        
        smartsweepvoltageend_label = tk.Label(master=frame_sweepconfig2, text = "Vend [V]")
        smartsweepvoltageend_label.pack(side='left', padx='5', pady='5')
    
        self.smartsweepvoltageend_entry = tk.Entry(master=frame_sweepconfig2, width=6)
        self.smartsweepvoltageend_entry.pack(side='left', padx='5', pady='5')
        self.smartsweepvoltageend_entry.insert(0, "15")
        
        smartsweepvotagestep_label = tk.Label(master=frame_sweepconfig2, text = "Vstep [V]")
        smartsweepvotagestep_label.pack(side='left', padx='5', pady='5')
    
        self.smartsweepvotagestep_entry = tk.Entry(master=frame_sweepconfig2, width=6)
        self.smartsweepvotagestep_entry.pack(side='left', padx='5', pady='5')
        self.smartsweepvotagestep_entry.insert(0, "0.1")
        
        smartsweepnplc_label = tk.Label(master=frame_sweepconfig2, text = "NPLC")
        smartsweepnplc_label.pack(side='left', padx='5', pady='5')
    
        self.smartsweepnplc_entry = tk.Entry(master=frame_sweepconfig2, width=6)
        self.smartsweepnplc_entry.pack(side='left', padx='5', pady='5')
        self.smartsweepnplc_entry.insert(0, "0.1")
    
    
        self.ivfilename_entry = tk.Entry(master=frame_sweepconfig2, width=32)
        self.ivfilename_entry.pack(side='left', padx='5', pady='5')
        #time.strftime('%Y-%m-%d-%H-%M-%S')
        self.ivfilename_entry.insert(0, "iv_&Y&m&d_&H&M&S.csv")
    
        self.ivmakefilename_label = tk.Label(master=frame_sweepconfig2, text = "")
        self.ivmakefilename_label.pack(side='left', padx='5', pady='5')
    
    
    
    
    
        self.smartsweepibroadcast_var = tk.IntVar(value=True)
        self.smartsweepibroadcast_checkbox = tk.Checkbutton(frame_sweepconfig2, text="broadcast", variable=self.smartsweepibroadcast_var)
        self.smartsweepibroadcast_checkbox.pack(side='left', padx='5', pady='5')
    
    
    
    
        self.smartsweepbestaetigen_Button = tk.Button(master=frame_sweepconfig2, text = "Sweep beginnen", state="disable",command=self.sweep_thread)
        self.smartsweepbestaetigen_Button.pack(side='left', padx='5', pady='5')






    def action_sweep(self):
#        self.threadLock.acquire()
                    
        self.able_buttons("disconnect")
        self.connect_button.config(state="disable")
        self.port_box_refresh_button.config(state="disable")
        
        
        
        self.mylabel_frame = tk.Toplevel()
        
        
        
        sw = self.mylabel_frame.winfo_screenwidth()
        sh = self.mylabel_frame.winfo_screenheight()
        
        rw = 500
        rh = 50
        
        x = (sw-rw) / 2
        y = (sh-rh) / 2
        
        self.mylabel_frame.geometry("%dx%d+%d+%d" %(rw,rh,x,y))

        
        top_label = tk.Label(self.mylabel_frame,text = "sweeping...")
        top_label.pack(side='bottom', padx='5', pady='5')
        

#        self.mylabel = tk.Label(self.mylabel_frame, text='Running loop').pack()

        self.p = ttk.Progressbar(self.mylabel_frame, orient=tk.HORIZONTAL, length=200,
                             mode='indeterminate')
        
        self.p.pack()
        self.p.start()
        
        
        print("start write:")
        self.writereadbytes('reset()')
        self.writereadbytes('errorqueue.clear()')
        self.writereadbytes('loadscript')             
        sleep(0.1)
        print("Initialisieren:")
    
        #initialisierung der SMU
        self.writereadbytes("smua.reset()")
        self.writereadbytes("delay(1)")
        self.writereadbytes("errorqueue.clear()")
        self.writereadbytes("display.clear()")
        self.writereadbytes("status.reset()")

    
        self.writereadbytes("voltageRange = nil		delay(0.1)	voltageRange = "+str(self.smartsweepvoltagerange_entry.get()))
        self.writereadbytes("currentRange = nil		delay(0.1) 	currentRange = "+str(self.smartsweepcurrentrange_entry.get()))
        self.writereadbytes("currentLimit = nil 	delay(0.1)	currentLimit = "+str(self.smartsweepcurrentlimit_entry.get()))
        self.writereadbytes("voltageStart = nil delay(0.1) voltageStart = "+str(self.smartsweepvotagestart_entry.get()))
        self.writereadbytes("voltageEnd   = nil delay(0.1) voltageEnd   = "+str(self.smartsweepvoltageend_entry.get()))
        self.writereadbytes("voltage_step  = nil delay(0.1) voltage_step  = "+str(self.smartsweepvotagestep_entry.get()))
        self.writereadbytes("nplc = nil delay(0.1) nplc = "+str(self.smartsweepnplc_entry.get()))#0.005
        #Bestimmung der Anzahl aufzunehmender Messwerte
        
        if int(self.smartsweepvotagestart_entry.get())>int(self.smartsweepvoltageend_entry.get()):
            self.writereadbytes("numberOfVals=math.ceil((voltageStart-voltageEnd)/voltage_step+1)")
        else:
            self.writereadbytes("numberOfVals=math.ceil((voltageEnd-voltageStart)/voltage_step+1)")
    
        print("Konfiguration:")
        #Konfiguration der SMU:
        self.writereadbytes("smua.source.highc = smua.DISABLE")#High Current -Mode
        self.writereadbytes("format.data = format.ASCII")# Daten werden als ASCII gespeichert
        self.writereadbytes("smua.source.func = smua.OUTPUT_DCVOLTS") #Set the source function to DC Volts (voltage scource)
        self.writereadbytes("smua.source.rangev = voltageRange	delay(0.1)")#Konfiguration auf SMU Übertragen
        self.writereadbytes("smua.source.levelv = voltageStart	delay(0.1)	")
        self.writereadbytes("smua.source.autorangev = smua.AUTORANGE_OFF")#Automatisches Wähelen des Messbereiches abschalten
        self.writereadbytes("smua.source.limiti = currentLimit")#Stombegrenzung einstellen
        self.writereadbytes("smua.sense = smua.SENSE_REMOTE")#SMU auf Remote-Sense schalten (4-Wire-Measurement)
        
        
    
        self.writereadbytes("smua.measure.rangei = currentRange")#Messbereich festlegen
        self.writereadbytes("smua.measure.nplc = nplc")	#Integrationszeit festlegen
        self.writereadbytes("smua.nvbuffer1.clear()") 						#Clear Buffer 1.
        self.writereadbytes("smua.nvbuffer1.appendmode = 1")					#Enable append buffer mode.
        self.writereadbytes("smua.nvbuffer1.collecttimestamps = 1")          #Zeiten mitschreiben
        self.writereadbytes("smua.nvbuffer1.collectsourcevalues = 1")        #gesetzte Spannungswerte Mitschreiben
        self.writereadbytes("smua.nvbuffer1.timestampresolution =  0.0001")#   --  0.000001 finest resolution is  1 µs
    

        print("Messung:")
    
        self.writereadbytes("display.screen=0")        # 0 or display.SMUA: Displays source-measure and compliance 
        self.writereadbytes("display.clear()")
        self.writereadbytes("display.settext(\" Messung\")")        
        self.writereadbytes("delay(0.5)") 
        sleep(0.5)
    
        
        self.writereadbytes("smua.source.output = smua.OUTPUT_ON")	#Schaltet Ausgang ein
        
        
        self.writereadbytes("display.smua.measure.func=display.MEASURE_DCAMPS")#Set the display to I-Measurement
        
    
        self.writereadbytes("smua.source.levelv =voltageStart")      #Ausgangsspannung wird auf Startwert gesetzt
        self.writereadbytes("delay(0.5)")                            # 0.5s delay um Einschwingvorgänge abzuwarten
        self.writereadbytes("timer.reset()")#internen Timer auf 0 setzen 
        self.writereadbytes("dt=nil")
        self.writereadbytes("delay(0.01)")
        self.writereadbytes("dt=timer.measure.t()")
        #Schleife für Sweep beginnen
        self.writereadbytes("for index = 1, numberOfVals do")		#Aufnahme der Messdaten
        #neuen Spannungswert berechnen
        if int(self.smartsweepvotagestart_entry.get())>int(self.smartsweepvoltageend_entry.get()):
            self.writereadbytes("smua.source.levelv = voltageStart - (index-1)*voltage_step")
        else:
            self.writereadbytes("smua.source.levelv = voltageStart + (index-1)*voltage_step")
    
    
        self.writereadbytes("smua.measure.i()")
        
        self.writereadbytes("delay(0.1)") #warten bis Messwerte eingestellt ist
        #self.writereadbytes("dt=timer.measure.t()")
        self.writereadbytes("smua.measure.overlappedi(smua.nvbuffer1)")#Messung durchführen und in Buffer schreiben
        self.writereadbytes("waitcomplete()")#Warten bis Messung abgeschlossen
        self.writereadbytes("end ")#Ende der Messung (Schleifenende)
        
        self.writereadbytes("dt=timer.measure.t()")
    
    
        sleep(1)
        print('start sweep')

        
        self.writereadbytes("smua.source.output = smua.OUTPUT_OFF")   #Schaltet Ausgang ab
        
        
        self.writereadbytes("display.clear()")	
        self.writereadbytes("display.settext(\"Yi, ich bin fertig\")")
        self.writereadbytes("print(\"END\")")

            

        self.writereadbytes('endscript')#Messscript beenden
    
        self.writereadbytes('script.run()')#Messscript ausführen

        self.zeit = time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time()))
       
        
        self.writereadbytes("waitcomplete()")



        while self.writereadbytes('') != "END":
            
            sleep(1)
            print("#", end = '') 
    
    
                   
                   
        self.nmax=320               # größte Anzahl aus der einmalig aufgerufenen readall Funktion

        self.numberOfValues = self.writereadbytes("print(tostring(numberOfVals))")
        self.numberOfValues = int(float(self.numberOfValues))
        print("numberOfValues:",self.numberOfValues)

        self.zykluszahl = self.numberOfValues/self.nmax
        print("self.zykluszahl: ", self.zykluszahl)
        if isinstance(self.zykluszahl,float):
            self.zykluszahl = int(self.zykluszahl) + 1
            print("self.zykluszahl: ", self.zykluszahl)
            
        
        measureTime=float(self.writereadbytes("print(tostring(dt))"))                
        print("Zeit:",measureTime)        
        
    
        self.t_array = []
        for value in range(1, self.zykluszahl + 1):
            print(value)
            
            if (value == 1):
                time_l = self.writereadbytesall("printbuffer(tostring(" + str(1) + ")" + ", tostring(" + str(int(value*(self.numberOfValues/self.zykluszahl))) + "), smua.nvbuffer1.timestamps)")
            
            elif (value == self.zykluszahl):
                time_l = self.writereadbytesall("printbuffer(tostring(" + str( 1  + int((value-1)*(self.numberOfValues/self.zykluszahl))) + ")" + ", tostring(" + str(int(value*(self.numberOfValues/self.zykluszahl))) + "), smua.nvbuffer1.timestamps)")    
          
            else:
                time_l = self.writereadbytesall("printbuffer(tostring(" + str( 1  + int((value-1)*(self.numberOfValues/self.zykluszahl))) + ")" + ", tostring(" + str(int(value*(self.numberOfValues/self.zykluszahl))) + "), smua.nvbuffer1.timestamps)")
            print("time_l: ", time_l)
            for item in time_l.split(','):
                self.t_array.append(float(item))
            
            
        sleep(0.1)
        
        print(self.t_array)
        
        timestamp = str(datetime.datetime.now()).split('.')[0]
    
        self.messaging(" > ".join([timestamp, "t_array"]), gui=True)  
        self.messaging(self.t_array, gui=True)

    
    
    
        self.v_array = []
        for value in range(1, self.zykluszahl + 1):
            print(value)
            
            if (value == 1):
                voltage_l = self.writereadbytesall("printbuffer(tostring(" + str(1) + ")" + ", tostring(" + str(int(value*(self.numberOfValues/self.zykluszahl))) + "), smua.nvbuffer1.sourcevalues)")
            
            elif (value == self.zykluszahl):
                voltage_l = self.writereadbytesall("printbuffer(tostring(" + str( 1  + int((value-1)*(self.numberOfValues/self.zykluszahl))) + ")" + ", tostring(" + str(int(value*(self.numberOfValues/self.zykluszahl))) + "), smua.nvbuffer1.sourcevalues)")    
          
            else:
                voltage_l = self.writereadbytesall("printbuffer(tostring(" + str( 1  + int((value-1)*(self.numberOfValues/self.zykluszahl))) + ")" + ", tostring(" + str(int(value*(self.numberOfValues/self.zykluszahl))) + "), smua.nvbuffer1.sourcevalues)")
            print("time_l: ", voltage_l)
            for item in voltage_l.split(','):
                self.v_array.append(float(item))
            
            
        sleep(0.1)
        
        print(self.v_array)
        
        timestamp = str(datetime.datetime.now()).split('.')[0]
    
        self.messaging(" > ".join([timestamp, "v_array"]), gui=True)  
        self.messaging(self.v_array, gui=True)
    

    
    
    
    
    
    

        self.i_array = []
        for value in range(1, self.zykluszahl + 1):
            print(value)
            
            if (value == 1):
                current_l = self.writereadbytesall("printbuffer(tostring(" + str(1) + ")" + ", tostring(" + str(int(value*(self.numberOfValues/self.zykluszahl))) + "), smua.nvbuffer1.readings)")
            
            elif (value == self.zykluszahl):
                current_l = self.writereadbytesall("printbuffer(tostring(" + str( 1  + int((value-1)*(self.numberOfValues/self.zykluszahl))) + ")" + ", tostring(" + str(int(value*(self.numberOfValues/self.zykluszahl))) + "), smua.nvbuffer1.readings)")    
          
            else:
                current_l = self.writereadbytesall("printbuffer(tostring(" + str( 1  + int((value-1)*(self.numberOfValues/self.zykluszahl))) + ")" + ", tostring(" + str(int(value*(self.numberOfValues/self.zykluszahl))) + "), smua.nvbuffer1.readings)")
            print("current_l: ", current_l)
            for item in current_l.split(','):
                self.i_array.append(float(item))
            
            
        sleep(0.1)
        
        print(self.i_array)
        
        timestamp = str(datetime.datetime.now()).split('.')[0]
    
        self.messaging(" > ".join([timestamp, "i_array"]), gui=True)  
        self.messaging(self.i_array, gui=True)
    
   




        self.make_filename()
        
        self.filenames.append(self.filename)
        
        self.csv_speichern()
        self.messaging(str(datetime.datetime.now()).split('.')[0] + " done smart_sweep_current ", gui=True, cli=True)

        self.get_Rsh_Mpp()
        self.Mpps.append(self.mpp)


        #print(threading.active_count(),'active_count()')

        df_2 = pd.DataFrame({'Mpp':self.Mpps,'filename':self.filenames})
        df_2.to_csv('MPP.csv',sep=',',index=0)
        
        
        self.able_buttons("connect")
        
        self.mylabel_frame.destroy()
#        self.threadLock.release()
        
        
    def sweep_thread(self):
        '''
        Spawn a new thread for running long loops in background
        '''
#        self.threadLock = threading.Lock()
#        self.threads = []
        
#        self.mylabel_frame = tk.Toplevel()
#        self.mylabel = tk.Label(self.mylabel_frame, text='Running loop').pack()
#        self.thread_queue = queue.Queue()
        #print(threading.active_count(),'active_count()_Beginn')
        self.new_thread =threading.Thread(target=self.action_sweep)
        self.new_thread.setDaemon(True)
        self.new_thread.start()
        #print(threading.active_count(),'active_count()_Ende')

#        self.mylabel_frame = tk.Toplevel()
#        self.mylabel = tk.Label(self.mylabel_frame, text='Running loop').pack()
#

#
#        self.mylabel_frame.after(100, self.listen_for_result)
        
        
        
        
        
    def listen_for_result(self):

        try:
            self.res = self.thread_queue.get(0)
#            self.mylabel.config(text='Loop terminated')
        except queue.Empty:
            self.mylabel_frame.after(100, self.listen_for_result)
        
        
        

    def make_filename(self):
        self.filename = self.ivfilename_entry.get()
        self.filename = self.filename.replace("&y", time.strftime('%y'))
        self.filename = self.filename.replace("&Y", time.strftime('%Y'))
        self.filename = self.filename.replace("&m", time.strftime('%m'))
        self.filename = self.filename.replace("&d", time.strftime('%d'))
        self.filename = self.filename.replace("&H", time.strftime('%H'))
        self.filename = self.filename.replace("&M", time.strftime('%M'))
        self.filename = self.filename.replace("&S", time.strftime('%S'))


    def csv_speichern(self):
    
        df_1 = pd.DataFrame({'time':self.t_array,'voltages':self.v_array,'currents':self.i_array})
        print(df_1)
        df_1.to_csv(self.filename + '.csv',sep=',',index=0)
    
    
        with open(self.filename + '.csv', 'r+', encoding = 'utf-8') as f:
            content = f.read()        
            f.seek(0, 0)
            
            f.write("Startzeit der Messung " + self.zeit + '\n' )
            f.write(content)

        f.close()





    def get_Rsh_Mpp(self):


        plt.title("I-V_Kennlinie",fontsize = 6)
        plt.xlabel("spannnung [V]", fontsize = 10)
        plt.ylabel("current [A]", fontsize = 10, verticalalignment='top',horizontalalignment='center')                                                                              
        
        
        
        files = sorted(glob.glob(self.filename + ".csv"))     #list of files
        print("processin raw files")
        

        for file in files:

            filename = basename(file).rsplit('.', 1)[0]      # each file in list of files                                                     
            print('\r'+ filename + "  ", flush = True)     # progress information
            
            
            
            with open(file) as f:    #'with' will auto close after loop
                #ax1.plot(121)
        
                csvreader = csv.reader(f, delimiter = ",", quotechar='"')     #read into csv object
        
                for line in range(2):      #skip header                             
                    next (csvreader)                                                                            
                voltage = []        #init lists      
                current = [] 
                power= []
                for row in csvreader:
                    voltage.append(float(row[1]))      #process each row
                    current.append(float(row[2]))        #extract column 
                    power.append(float(row[1])*(float(row[2])-float(self.smartsweepshortcircutcurrent_entry.get()))) # 9 = Isc for Pseudo MPP
                        
        
                plt.plot(voltage, current, 'b', label=filename)
                #plt.plot(voltage, power, 'k.--', label=filename)
                plt.legend(loc=2,fontsize=3)
                print("power: ", power)
            
            
            self.mpp=np.min(power)
            u2=0.5
            u1=0
            
            u_2 = np.linspace(u2,u2,len(current))     # Isc auf dem Diagramm anzeigen
            u_1 = np.linspace(u1,u1,len(current))
            
        
            
            i_dx2 = (np.argwhere(np.diff(np.sign(u_2 - voltage))).flatten())[-1]
#            print("i_dx2", i_dx2)
            
            #sign()是Python的Numpy中的取数字符号（数字前的正负号）的函数。
            #np.diff函数总结下就是每行的后一个值减去前一个，然后放到一个新的数组里面
            # np.argwhere( a )
            #返回非 0的数组元组的索引，其中a是要索引数组的条件。entsprchende X-wert einsammeln
            #a.flatten()：a是个数组，a.flatten()就是把a降到一维，默认是按行的方向降 。
            #Find the indices of array elements that are non-zero, grouped by element.
#            n=0
#            summ_2=0
#            summ_1=0
#            for i in i_dx2:
#                summ_2= summ_2 + i
#                n=n+1
#            i_dx2=summ_2/n
#            i_dx2=int(i_dx2)

            i_dx1 = (np.argwhere(np.diff(np.sign(u_1 - voltage))).flatten())[0] # wenn u_1 = 0 ist<!!!!
#            print("i_dx1", i_dx1)
            
            # entsprchende X-wert einsammeln
#            for i in i_dx1:
#                summ_1= summ_1 + i
#                n=n+1
#            i_dx1=summ_1/n
#            i_dx1=int(i_dx1)
            
             
            
            
            
            
            print("i_dx2", i_dx2)
            print("i_dx1", i_dx1)
            
            
            print("idx_2:", np.int(i_dx2))
            print("idx_1:", np.int(i_dx1))


            i2=float(np.array(current,dtype=np.float)[i_dx2])
            print("current_2: ",i2)
            i1=float(np.array(current,dtype=np.float)[i_dx1])
            print("current_1:", i1)
            
            i_2 = np.linspace(i2,i2,len(voltage))     # Isc auf dem Diagramm anzeigen
            i_1 = np.linspace(i1,i1,len(voltage))        
            
            
            
            
            u2=float(np.array(voltage,dtype=np.float)[i_dx2])
            u1=float(np.array(voltage,dtype=np.float)[i_dx1])
            print("voltage_2:",u2)
            print("voltage_1:",u1)
            
            
            
            plt.plot(u_2,current, label= filename)   #actual plot
            plt.plot(u_1,current, label= filename)   #actual plot
            
            
            plt.plot(voltage,i_2 , label= filename)   #actual plot
            plt.plot(voltage,i_1 , label= filename)   #actual plot
            
        
            
            
            plt.plot(np.array(voltage,dtype=np.float)[i_dx2], np.array(current,dtype=np.float)[i_dx2], 'ro')  # kritische Punkte  auf dem Diagramm anzeigen          
            plt.plot(np.array(voltage,dtype=np.float)[i_dx1], np.array(current,dtype=np.float)[i_dx1], 'ro')  # kritische Punkte  auf dem Diagramm anzeigen  
            
            
            
        r_sh=(u2 - u1)/(i2 - i1)


        
        print("Rsh:", r_sh)
        print("Mpp:", self.mpp*(-1))  
        i_dxu = (np.argwhere(np.diff(np.sign(np.linspace(self.mpp,self.mpp,len(power)) - power))).flatten())[-1]
        print("i_dxu: ", i_dxu)  
        i_dxu=int(i_dxu)

        
        print("i_dxu", i_dxu)
 
        
        plt.plot(np.array(voltage,dtype=np.float)[i_dxu], np.array(current,dtype=np.float)[i_dxu], 'ro')  # kritische Punkte  auf dem Diagramm anzeigen
        
        plt.savefig(filename + ".png", dpi = 300)    #save plot as file
        plt.show()       #present plot 






    def gui_automation(self):
        #frame_automation
        
        frame_automation  = tk.LabelFrame(self.parent, text = "automation settings", bd = 3, relief = 'groove')
        frame_automation.pack(side='top', fill='x')   # connect frame
        
        # sub_frame frame_starttimer
        frame_starttimer = tk.Frame(master=frame_automation)
        frame_starttimer.pack(side='top', fill='x') # meas filename
        
        self.starttimer_button = tk.Button(master=frame_starttimer, text = "start timer", width = 10, command = self.action_startbutton)
        self.starttimer_button.pack(side='left', padx='5', pady='5')
        self.starttimer_button.config(state="disable")
    
        self.stoptimer_button = tk.Button(master=frame_starttimer, text = "stop timer", width = 10, command = self.action_stopbutton)
        self.stoptimer_button.pack(side='left', padx='5', pady='5')
        self.stoptimer_button.config(state="disable")
    
        self.starttimer_entry = tk.Entry(master=frame_starttimer, width=18)
        self.starttimer_entry.pack(side='left', padx='5', pady='5')
        self.starttimer_entry.insert(0, (datetime.datetime.now()+datetime.timedelta(seconds = 5)).strftime('%Y-%m-%d %H:%M:%S'))
        starttimerduration_label = tk.Label(master=frame_starttimer, text = "duration")
        starttimerduration_label.pack(side='left', padx='5', pady='5')
    
        self.starttimerduration_entry = tk.Entry(master=frame_starttimer, width=10)
        self.starttimerduration_entry.pack(side='left', padx='5', pady='5')
        self.starttimerduration_entry.insert(0, "00:10:00")
        
        starttimerendtxt_label = tk.Label(master=frame_starttimer, text = "ending at")
        starttimerendtxt_label.pack(side='left', padx='5', pady='5')
    
        self.starttimerending_entry = tk.Entry(master=frame_starttimer, width=18)
        self.starttimerending_entry.pack(side='left', padx='5', pady='5')
        self.starttimerending_entry.insert(0, "")   
        
        # sub_frame frame_autosweep
        frame_autosweep = tk.Frame(master=frame_automation)
        frame_autosweep.pack(side='top', fill='x') # meas filename   
            
    
        self.dosweep_var = tk.IntVar(value = True)
        dosweep_checkbox = tk.Checkbutton(master=frame_autosweep, text="sweep i", variable=self.dosweep_var)
        dosweep_checkbox.pack(side='left', padx='5', pady='5')
        dosweep_label = tk.Label(master=frame_autosweep, text='every')
        dosweep_label.pack(side='left', padx='5', pady='5')
    
        self.dosweep_entry = tk.Entry(master=frame_autosweep, width=10)
        self.dosweep_entry.pack(side='left', padx='5', pady='5')
        self.dosweep_entry.insert(0, "00:02:00")
        
        dosweepnext_label = tk.Label(master=frame_autosweep, text='next ')
        dosweepnext_label.pack(side='left', padx='5', pady='5')
    
        self.dosweepnext_entry = tk.Entry(master=frame_autosweep, width=18)
        self.dosweepnext_entry.pack(side='left', padx='5', pady='5')
        self.dosweepnext_entry.insert(0, self.starttimer_entry.get())
        self.dosweepnext_entry.config(state="disable")
        
        MPP_file_label = tk.Label(master=frame_autosweep, text='MPP_file')
        MPP_file_label.pack(side='left', padx='5', pady='5')
    
        self.MPP_file_entry = tk.Entry(master=frame_autosweep, width=35)
        self.MPP_file_entry.pack(side='left', padx='5', pady='5')
        self.MPP_file_entry.insert(0, "MPP.csv")






    def gui_listbox(self):
        frame_listbox  = tk.Frame(self.parent, bd = 3, relief = 'groove')
        frame_listbox.pack(side='top', fill='x')
    
        # listbox + scrollbar
        frame_listbox_1 = tk.Frame(master=frame_listbox)
        frame_listbox_1.pack(side='top', fill='x')
    
        listbox_scrollbar_y = tk.Scrollbar(frame_listbox_1)
        listbox_scrollbar_y.pack(side='right', fill='y')
        
        listbox_scrollbar_x = tk.Scrollbar(frame_listbox_1, orient='horizontal')
        listbox_scrollbar_x.pack(side='bottom', fill='x')
        

        self.listbox_listbox = tk.Listbox(master=frame_listbox_1, width=100, height=16, yscrollcommand=listbox_scrollbar_y.set, xscrollcommand=listbox_scrollbar_x.set, selectmode='EXTENDED')
        self.listbox_listbox.pack(side='left', padx='5', pady='5')
        
        listbox_scrollbar_y.config(command=self.listbox_listbox.yview)
        listbox_scrollbar_x.config(command=self.listbox_listbox.xview)
    
        #clear  button
        frame_listbox_2 = tk.Frame(master=frame_listbox)
        frame_listbox_2.pack(side='top', fill='x')

        self.clear_button = tk.Button(master=frame_listbox_2, text = "Clear", width = 10, command = self.action_clear)
        self.clear_button.pack(side='left', padx='5', pady='5')


    def action_clear(self):
        self.listbox_listbox.delete(0, tk.END)










    def action_startbutton(self):
        self.send_button.config(state="disable")
        self.starttimer_button.config(state="disable")
        self.starttimer_button.config(text="waiting")
        self.stoptimer_button.config(state="normal")
        self.starttimer_entry.config(state="disable")
        self.starttimerduration_entry.config(state="disable")
        self.dosweepnext_entry.config(state="disable")
        self.dosweep_entry.config(state="disable")
        self.port_box_refresh_button.config(state="disable")
        self.messaging("waiting for timer at " + str(self.starttimer_entry.get()), cli=True, gui=True)
    
        '''
        starttimer_entry 
        starttimerduration_label 
        starttimerduration_entry 
        starttimerendtxt_label 
        starttimerending_label 
        '''
    
    
    
    def action_stopbutton(self):
        self.send_button.config(state="normal")
        self.starttimer_button.config(state="normal")
        self.stoptimer_button.config(state="disable")
        self.starttimer_entry.config(state="normal")
        self.starttimerduration_entry.config(state="normal")
        self.dosweepnext_entry.config(state="normal")
        self.dosweep_entry.config(state="normal")
        self.smartsweepbestaetigen_Button.config(state="normal")
        self.disconnect_button.config(state="normal")
        
        self.messaging("timer stopped at " + time.strftime('%Y-%m-%d %H:%M:%S'), cli=True, gui=True)
    #    if starttimer_button.cget('text') == "testing":
    #        globalswitch(False)
    #        pass
        self.starttimer_button.config(text = "start timer")
    
    
    
    def action_starttest(self):
        self.starttimer_button.config(state="disable")
        self.starttimer_button.config(text="testing")
        self.stoptimer_button.config(state="normal")
        self.starttimer_entry.config(state="disable")
        self.starttimerduration_entry.config(state="disable")
        self.messaging("start test at " + str(self.starttimer_entry.get()), cli=True, gui=True)
        self.smartsweepbestaetigen_Button.config(state="disable")
    #    action_setv()
    #    action_seti()
    #    globalswitch(True)
        pass
    
    
    
    
    @staticmethod
    def checkvalid(self, re):
        if (re.match(self.get())):
            self.config(fg = 'green')
            return True
        else:
            self.config(fg = 'red')
            return False
    @staticmethod
    def checkValidRange(self, re, lower=0, upper=32000):
        if (re.match(self.get())):
            if (float(self.get()) >= lower and float(self.get()) <= upper):
                self.config(fg = 'green')
                return True
            else:
                self.config(fg = 'red')
                return False
        else:
            self.config(fg = 'red')
            return False
    @staticmethod
    def updatenext(self, interval):
        if datetime.datetime.strptime(str(self.get()), '%Y-%m-%d %H:%M:%S') < datetime.datetime.now():
            interval_array = interval.split(":")
            interval_seconds = int(interval_array[0])*3600 + int(interval_array[1])*60 + int(interval_array[2])
            donext = datetime.datetime.now() + datetime.timedelta(seconds = interval_seconds) # now + interval
            self.config(state="normal")
            self.delete(0, tk.END)
            self.insert(0, donext.strftime('%Y-%m-%d %H:%M:%S'))
            self.config(state="disable")
    
            return True
        else:
            return False
    
    
    
    
    def gui_status(self):
        frame_status = tk.Frame(self.parent, bd = 3, relief = 'groove')
        frame_status.pack(side='top', fill='x')   # status frame
        # status frame

        self.status_label = tk.Label(master=frame_status, text = "status")
        self.status_label.pack(side='right', padx='5', pady='5')
        self.status_label.config(text = self.port_box.get())




    def tick(self):

        # refresh gui and inputs, also watch for triggers
        self.status_label.config(text=time.strftime('%Y-%m-%d %H:%M:%S'))
        #[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) (2[0-3]|[01][0-9]):[0-5][0-9]
    
        if self.starttimer_button.cget('text') == "start timer" and (self.checkvalid(self.starttimer_entry, re_datetime) and (self.checkvalid(self.starttimerduration_entry, re_timestamp))):
            
            if datetime.datetime.strptime(str(self.starttimer_entry.get()), '%Y-%m-%d %H:%M:%S') < datetime.datetime.now():
                
                self.starttimer_entry.delete(0, tk.END)
                self.starttimer_entry.insert(0, time.strftime('%Y-%m-%d %H:%M:%S'))
                pass
    
            
            timestart = datetime.datetime.strptime(str(self.starttimer_entry.get()), '%Y-%m-%d %H:%M:%S')
            td = self.starttimerduration_entry.get().split(":")
            interval = int(td[0])*3600 + int(td[1])*60 + int(td[2])
            timerending = timestart + datetime.timedelta(seconds = interval)
            self.starttimerending_entry.config(state="normal")
            self.starttimerending_entry.delete(0, tk.END)
            self.starttimerending_entry.insert(0, timerending.strftime('%Y-%m-%d %H:%M:%S'))
            self.starttimerending_entry.config(state="disable")
            
    
        if self.starttimer_button.cget('text') == "testing":
            
#            self.able_buttons("disconnect")
#            self.connect_button.config(state="disable")
            if self.dosweep_var.get():
                if self.updatenext(self.dosweepnext_entry, self.dosweep_entry.get()):
                    self.messaging("sweep triggered at " + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), cli=True, gui=True)
#                    self.action_startbutton()
                    self.sweep_thread()
                else:
                    self.able_buttons("disconnect")
                    self.connect_button.config(state="disable")
                    self.port_box_refresh_button.config(state="disable")
                    
#                    df_2 = pd.DataFrame({'Mpp':self.Mpps,'filename':self.filenames})
#                    df_2.to_csv('MPP.csv',sep=',',index=0)
     
            
            pass
            if datetime.datetime.strptime(str(self.starttimerending_entry.get()), '%Y-%m-%d %H:%M:%S') < datetime.datetime.now():
                self.action_stopbutton() # stop when test duration is over
 
        
        if self.starttimer_button.cget('text') == "waiting":
            if datetime.datetime.strptime(str(self.starttimer_entry.get()), '%Y-%m-%d %H:%M:%S') < datetime.datetime.now():
    
                self.action_starttest()
        
        root.after(200, self.tick)


    def gui_check_valid(self):


        self.checkvalid(self.dosweep_entry, re_timestamp)
    
    
        self.checkValidRange(self.smartsweepvoltageend_entry, re_float, 0, 40)
        self.checkValidRange(self.smartsweepvotagestart_entry, re_float, 0, 40)
    
        self.checkValidRange(self.smartsweepvotagestep_entry, re_float, 0, 1)
    
        
        self.checkValidRange(self.smartsweepvoltagerange_entry, re_float,0, 40)
    
        self.checkValidRange(self.smartsweepcurrentrange_entry, re_float,0, 10)
    
        self.checkValidRange(self.smartsweepcurrentlimit_entry, re_float,0, 10)
        
        self.checkValidRange(self.smartsweepshortcircutcurrent_entry, re_float,0, 50)
        
        self.checkValidRange(self.smartsweepnplc_entry, re_float,0, 1)




    
root = tk.Tk()

sw = root.winfo_screenwidth()
sh = root.winfo_screenheight()

rw = 1000
rh = 650

x = (sw-rw) / 2
y = (sh-rh) / 2

root.geometry("%dx%d+%d+%d" %(rw,rh,x,y))



def main(): 
    
    my_keithly = Keithley_gui(root)

    my_keithly.gui_connect()
    my_keithly.gui_globalsettings()
    my_keithly.gui_manual()
    my_keithly.gui_automation()
    my_keithly.gui_listbox()
    my_keithly.gui_status()
    my_keithly.gui_check_valid()
    my_keithly.tick()
    root.mainloop()


if __name__ == '__main__':
    main()
