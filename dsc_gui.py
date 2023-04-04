# modified by Arne Groh
# for Python 3 and VHF
# Apr 2023
#
# forced from
#
# Wire2waves Ltd
# DSC Generator & Modulator
# Generic GUI


from tkinter import *
from dsc_functions import *
import threading
import queue
import time
from datetime import datetime,timezone

version = "v1.0/ag"

now = datetime.now(timezone.utc)
now_utc = now.strftime("%H%M")

class Application(Frame):
    def __init__(self, master):
        """ Initialize frame"""
        Frame.__init__(self, master)
        self.grid()
        self.create_widgets()
        self.dscqueue = queue.Queue()
        self.tunequeue = queue.Queue()
        self.cwqueue = queue.Queue()
        self.tunequeue.put(0)
        self.dscqueue.put(0)
        self.cwqueue.put(0)
        t1 = threading.Thread(target = self.tune)
        t1.daemon = True
        t1.start()
        c1 = threading.Thread(target = self.send_cwid)
        c1.daemon = True
        c1.start()
        d1 = threading.Thread(target = self.send_dsc)
        d1.daemon = True
        d1.start()
        
        
    def create_widgets(self):
        
        ###### Normal GUI Widgets
        #
        self.to_l = Label(self, width = 15, text = "To MMSI", fg = 'red').grid(row = 0, column = 0, sticky = W)
        self.to_mmsi_e = Entry(self, width = 10, fg = 'red')
        self.to_mmsi_e.grid(row = 0, column = 1, padx = 5, pady = 5, sticky = W)
        self.to_mmsi_e.insert(0, "111111111")
        
        
        self.from_l = Label(self, width = 15, text = "Self MMSI", fg = 'blue').grid(row = 1, column = 0, sticky = W)
        self.from_mmsi_e = Entry(self, width = 10, fg = 'blue')
        self.from_mmsi_e.grid(row = 1, column = 1, padx = 5, pady = 5, sticky = W)
        self.from_mmsi_e.insert(0, "333333333")
        
        self.utc_l = Label(self, width = 15, text = "UTC", fg = 'green').grid(row = 2, column = 0, sticky = W)
        self.utc_e = Entry(self, width = 4, fg = 'green')
        self.utc_e.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = W)
        self.utc_e.insert(0, now_utc)
        
        
        ###################
        area_f = Frame(self, relief = GROOVE, borderwidth = 2, pady = 5)
        area_f.grid(row = 3, column = 0, columnspan = 5, padx = 5, pady = 5, sticky = W+E)
        
        self.ns = StringVar()
        self.ew = StringVar()
        
        self.area_l = Label(area_f, width = 15, text = "Deg Lat",).grid(row = 2, column = 0, sticky = W)
        
        self.area_lat_e = Entry(area_f, width = 4, fg = 'red')
        self.area_lat_e.grid(row = 2, column = 1, padx = 5, pady = 5, sticky = W)
        self.area_lat_e.insert(0, "50")
        
        self.area_n_r = Radiobutton(area_f, variable = self.ns, text = "N", value = "n")
        self.area_n_r.grid(row = 2, column = 2)
        self.area_s_r = Radiobutton(area_f, variable = self.ns, text = "S", value = "s")
        self.area_s_r.grid(row = 2, column = 3)
        self.area_n_r.invoke()
       
        Label(area_f, width = 8, text = "Deg Lon").grid(row = 2, column = 4, sticky = E)
        
        self.area_lon_e = Entry(area_f, width = 4, fg = 'red')
        self.area_lon_e.grid(row = 2, column = 5, padx = 5, pady = 5, sticky = W)
        self.area_lon_e.insert(0, "010")
        
        self.area_w_r = Radiobutton(area_f, variable = self.ew, text = "W", value = "w")
        self.area_w_r.grid(row = 2, column = 6)
        self.area_s_r = Radiobutton(area_f, variable = self.ew, text = "E", value = "e")
        self.area_s_r.grid(row = 2, column = 7)
        self.area_s_r.invoke()
        
        self.area_l = Label(area_f, width = 15, text = "Min Lat",).grid(row = 3, column = 0, sticky = W)
        self.area_ns_e = Entry(area_f, width = 4, fg = 'red')
        self.area_ns_e.grid(row = 3, column = 1, padx = 5, pady = 5, sticky = W)
        self.area_ns_e.insert(0, "12")
        self.area_ns_l = Label(area_f, width = 7, text = 'N --> S').grid(row = 3, column = 2)
        
        Label(area_f, width = 8, text = "Min Lon").grid(row = 3, column = 4, sticky = E)
        
        self.area_we_e = Entry(area_f, width = 5, fg = 'red')
        self.area_we_e.grid(row = 3, column = 5, padx = 5, pady = 5, sticky = W)
        self.area_we_e.insert(0, "34")
        self.area_we_l = Label(area_f, width = 7, text = 'W --> E').grid(row = 3, column = 6)
        
        freq_f = Frame(self, relief = GROOVE, borderwidth = 2, pady = 5)
        freq_f.grid(row = 4, column = 0, columnspan = 3, padx = 5, pady = 5, sticky = W+E)
                
        self.rxchan_l = Label(freq_f, width = 15, text = "RX VHF Channel",).grid(row = 1, column = 0, sticky = W)
        self.rxchan_e = Entry(freq_f, width = 8, fg = 'red',  justify = RIGHT)
        self.rxchan_e.grid(row = 1, column = 1, padx = 2, pady = 2, sticky = E)
        self.rxchan_e.insert(0, "069")

        self.txchan_l = Label(freq_f, width = 15, text = "TX VHF Channel",).grid(row = 2, column = 0, sticky = W)
        self.txchan_e = Entry(freq_f, width = 8, fg = 'red',  justify = RIGHT)
        self.txchan_e.grid(row = 2, column = 1, padx = 2, pady = 2, sticky = E)
        self.txchan_e.insert(0, "069")       
        
        self.freq_var = IntVar()
        self.freq_used = Checkbutton(freq_f, text = "Include?", variable = self.freq_var)
        self.freq_used.grid(row = 3, column = 1)
        
        self.fmt = StringVar()
        self.fmt_l = Label(self, width = 15, text = "Format").grid(row = 5, column = 0, sticky = W)
        self.sel_r = Radiobutton(self, text = "Sel", variable = self.fmt, value = "sel")
        self.sel_r.grid(row = 5, column = 1, sticky = W)
        self.all_r = Radiobutton(self, text = "All Ships", variable = self.fmt, value = "all ships")
        self.all_r.grid(row = 5, column = 2, sticky = W)
        self.area_r = Radiobutton(self, text = "Area", variable = self.fmt, value = "area")
        self.area_r.grid(row = 5, column = 3, sticky = W)
        self.group_r = Radiobutton(self, state=DISABLED, text = "Group", variable = self.fmt, value = "group")
        self.group_r.grid(row = 5, column = 4, sticky = W)
        self.group_r = Radiobutton(self, text = "Distress", variable = self.fmt, value = "dis")
        self.group_r.grid(row = 5, column = 4, sticky = W)
        #self.group_r = Radiobutton(self, state=DISABLED, text = "Auto", variable = self.fmt, value = "auto")
        #self.group_r.grid(row = 5, column = 6, sticky = W)
        
        self.sel_r.invoke()
        
        self.cat = StringVar()
        
        self.cat_l = Label(self, width = 15, text = "Category").grid(row = 6, column = 0, sticky = W)
        self.saf_r = Radiobutton(self, text = "Routine", variable = self.cat, value = "rtn")
        self.saf_r.grid(row = 6, column = 1, sticky = W)
        self.saf_r = Radiobutton(self, text = "Safety", variable = self.cat, value = "saf")
        self.saf_r.grid(row = 6, column = 2, sticky = W)
        self.urg_r = Radiobutton(self, text = "Urgency", variable = self.cat, value = "urg")
        #self.urg_r = Radiobutton(self, state=DISABLED, text = "Urgency", variable = self.cat, value = "urg")
        self.urg_r.grid(row = 6, column = 3, sticky = W)
        self.dis_r = Radiobutton(self, text = "Distress", variable = self.cat, value = "dis")
        #self.dis_r = Radiobutton(self, state=DISABLED, text = "Distress", variable = self.cat, value = "dis")
        self.dis_r.grid(row = 6, column = 4, sticky = W)
        
        self.saf_r.invoke()
        
        
        self.tc1_var = StringVar()
        self.tc1_l = Label(self, width = 15, text = "TC1").grid(row = 7, column = 0, sticky = W)
        self.tc1_sp = Spinbox(self, width = 15, textvariable = self.tc1_var, readonlybackground = 'white', state = "readonly", values = ("test", "f3e", "f3edup", "poll", "unable", "end", "data", "j3e", "disack", "disrel", "fec", "arq", "test", "pos", "noinf"), wrap = True)
        self.tc1_sp.grid(row = 7, column = 1, columnspan = 3, sticky = W)
        
        
        self.tc2_var = StringVar()
        self.tc2_l = Label(self, width = 15, text = "TC2").grid(row = 8, column = 0, sticky = W)
        self.tc2_sp = Spinbox(self, width = 15, readonlybackground = 'white', textvariable = self.tc2_var, state = "readonly", values = ("noinf", "no reason", "congestion", "busy", "queue", "barred", "no oper", "temp unav", "disabled", "unable channel", "unable mode", "conflict", "medical", "payphone", "fax", "noinf"), wrap = True)
        self.tc2_sp.grid(row = 8, column = 1, columnspan = 3, sticky = W)
        
        self.msg1_var = StringVar()
        self.msg1_l = Label(self, width = 20, text = "MSG1 nature of distress").grid(row = 9, column = 0, sticky = W)
        self.msg1_sp = Spinbox(self, width = 41, readonlybackground = 'white', textvariable = self.msg1_var, state = "readonly", values = ("undesignated distress", "fire, explosion", "flooding", "collision", "grounding", "listing, in danger of capsizing", "sinking", "disabled and adrift", "abandoning ship", "piracy/armed robbery attack", "person overboard", "emergency position-indicating radiobeacon (EPIRB) emission"), wrap = True)
        self.msg1_sp.grid(row = 9, column = 1, columnspan = 3, sticky = W)
        
        self.eosv = StringVar()
        self.eos_l = Label(self, width = 15, text = "EOS").grid(row = 10, column = 0, sticky = W)
        self.req_r = Radiobutton(self, text = "REQ", variable = self.eosv, value = "req")
        self.req_r.grid(row = 10, column = 1, sticky = W)
        self.ack_r = Radiobutton(self, text = "ACK", variable = self.eosv, value = "ack")
        self.ack_r.grid(row = 10, column = 2, sticky = W)
        self.eos_r = Radiobutton(self, text = "EOS", variable = self.eosv, value = "eos")
        self.eos_r.grid(row = 10, column = 3, sticky = W)
        self.req_r.invoke()
        
        
        self.go_b = Button(self, text = "Send DSC", command = self.dscqueue_on)
        self.go_b.grid(row = 11, column = 0, sticky = W+E)
        
        
        self.tune_b = Button(self, text = "Tune", command = self.tunequeue_on)
        self.tune_b.grid(row = 14, column = 0, sticky = W+E)
        
        '''
        self.sendcw = IntVar()
        self.cw_cb = Checkbutton(self, text = "CWID", variable = self.sendcw)
        self.cw_cb.grid(row = 10, column = 1)
        self.cw_cb.deselect()
        '''
        
        self.cw_call_e = Entry(self)
        self.cw_call_e.grid(row = 15, column = 1, columnspan = 2)
        self.cw_call_e.insert(0, "qtc")
        
        self.cw_b = Button(self, text = "Send CW ->", command = self.cwqueue_on)
        self.cw_b.grid(row = 15, column = 0, sticky = W+E)
        
        self.test_b = Button(self, text = "Setup Test Call", command = self.test)
        self.test_b.grid(row = 16, column = 0, sticky = W+E)
        
        self.dsc_title = Label(self, text = "Sending DSC Symbols: " , fg = 'blue').grid(row = 17, column = 0)
        
        dsc_call_f = Frame(self, relief = GROOVE, borderwidth = 2, pady = 5)
        dsc_call_f.grid(row = 18, column = 0, columnspan = 5, padx = 5, pady = 5, sticky = W+E)
        
        
        self.dsc_label = StringVar()
        self.dsc_l = Label(dsc_call_f, textvariable = self.dsc_label, fg = 'blue', height = 3, wraplength = 350, anchor = W)
        self.dsc_l.grid(row = 0, column = 0)
        ####
        
        
    def test(self):
        eos_symbol = 127
        cat_symbol = 108
        fmt_symbol = 120
        tc1_symbol = 118
        tc2_symbol = 126
        self.eosv.set("req")
        self.cat.set("saf")
        self.fmt.set("sel")
        self.tc1_var.set("test")
        self.tc2_var.set("noinf")
        now = datetime.now(timezone.utc)
        now_utc = now.strftime("%H%M")
        self.utc_e.delete(0,END)
        self.utc_e.insert(0, now_utc)
        self.freq_var.set(False)
        
        
    def tunequeue_on(self):
        print ("tune queue on")
        self.tunequeue.put(1)
    def tunequeue_off(self):
        print ("tune queue off")
        self.tunequeue.put(0)
        
        
    def tune(self):
        
        while True:
            t_on = self.tunequeue.get()
            if t_on == 1:
                
                pwr = 0.7
                tune_carrier(pwr)
                self.tunequeue_off()
    
    
    def cwqueue_on(self):
        print ("cw queue on")
        self.cwqueue.put(1)
    def cwqueue_off(self):
        print ("cw queue off")
        self.cwqueue.put(0)
    
    def send_cwid(self):
        while True:
            c_on = self.cwqueue.get()
            if c_on == 1:
                
                pwr = 0.7
                #sendcw = self.sendcw.get()
                #print ("sendcw ", sendcw)
                #if sendcw:
                call = self.cw_call_e.get().upper()
                cwid(call, pwr)
                self.cwqueue_off()
                #else:
                #    return
            
    def dscqueue_on(self):
        print ("txqueue On")
        self.dscqueue.put(1)
    def dscqueue_off(self):
        print ("txqueue Off")
        self.dscqueue.put(0)
     
    def send_dsc(self):
        
        while True:
            #time.sleep(1)
            go = self.dscqueue.get()
            
            if go == 1:
        
                a_mmsi = self.to_mmsi_e.get()
                s_mmsi = self.from_mmsi_e.get()
                fmt = self.fmt.get()
                cat = self.cat.get()
                tc1 = self.tc1_sp.get()
                tc2 = self.tc2_sp.get()
                msg1 = self.msg1_sp.get()
                utc1 = self.utc_e.get()[0:2]
                utc2 = self.utc_e.get()[2:4]
                #utc = self.utc_e.get()
                eos = self.eosv.get()
                ns = self.ns.get()
                ew = self.ew.get()
                pwr = 0.7
                quadrant = area_table[ns + ew]
                area = quadrant + self.area_lat_e.get().rjust(2,'0') + self.area_ns_e.get().rjust(2,'0') + self.area_lon_e.get().rjust(3,'0') + self.area_we_e.get().rjust(2, '0')

                rxchan = self.rxchan_e.get().rjust(3,'0')
                drxchanh = rxchan[0:1].rjust(1,'0')
                drxchant = rxchan[1:2].rjust(1,'0')
                drxchanu = rxchan[2:3].rjust(1,'0')

                txchan = self.txchan_e.get().rjust(3,'0')
                dtxchanh = txchan[0:1].rjust(1,'0')
                dtxchant = txchan[1:2].rjust(1,'0')
                dtxchanu = txchan[2:3].rjust(1,'0')


                #print ("freq info ", "9" + "0" + "1" + drxchanh + drxchant + drxchanu + dtxchanh + dtxchant + dtxchanu)
                #print ("freq info ", "9" + "0" + "1" + drxchanh + drxchant + drxchanu + "9" + "0" + "1" + dtxchanh + dtxchant + dtxchanu)
       
                try:
                    dfreq = int( "9" + "0" + "1" + drxchanh + drxchant + drxchanu + "9" + "0" + "1" + dtxchanh + dtxchant + dtxchanu )
                    dfreq = str( "9" + "0" + "1" + drxchanh + drxchant + drxchanu + "9" + "0" + "1" + dtxchanh + dtxchant + dtxchanu )
                except:
                    return
        
        
                if len(a_mmsi) != 9:
                    continue
                if len(s_mmsi) != 9:
                    continue
        
                fmt_symbol = int(fmt_symbol_dict[fmt])
                cat_symbol = int(cat_symbol_dict[cat])
                tc1_symbol = int(tc1_symbol_dict[tc1])
                tc2_symbol = int(tc2_symbol_dict[tc2])
                msg1_symbol = int(msg1_symbol_dict[msg1])
                utc1_symbol = int(utc1)
                utc2_symbol = int(utc2)
                eos_symbol = int(eos_symbol_dict[eos])
                
                # convert the MMSI 9-digits into a list of 2-digit symbols
                if fmt_symbol == 102:# if  "Area"
                    
                    a_symbol = area_symbol(area)
                    #print (dfreq)
                    if len(dfreq) > 12:
                        continue
                    data_symbol = freq_symbol(dfreq)
                    print (data_symbol)
                    eos_symbol = 127
                    cat_symbol = 108
                    tc1_symbol = 109
                    self.freq_var.set(True)
                    self.eosv.set("eos")
                    self.cat.set("saf")
                    self.tc1_var.set("j3e")
                    s_symbol = mmsi_symbol(s_mmsi)
                   
                    
                    dsc_call = build_call(fmt_symbol, a_symbol, cat_symbol, s_symbol, tc1_symbol, tc2_symbol, data_symbol, eos_symbol)
               
                    self.dsc_label.set(dsc_call)
                    self.dscqueue_off()
                    transmit_dsc(dsc_call, pwr) 
                    continue
                    #return
                    
                else:
                    a_symbol = mmsi_symbol(a_mmsi)
                    data_symbol = [ 126, 126, 126, 126, 126, 126 ]
        

                if fmt_symbol == 112:# if  "Distress"
                    
                    a_symbol = area_symbol(area)
                    #print (quadrant)
    
                    eos_symbol = 127
                    cat_symbol = 108
                    tc1_symbol = 109
                    data_symbol = [ 100 ]
                    self.freq_var.set(True)
                    self.eosv.set("eos")
                    self.cat.set("dis")
                    self.tc1_var.set("j3e")
                    s_symbol = mmsi_symbol(s_mmsi)
                   
                    
                    dsc_call = build_call(fmt_symbol, s_symbol, msg1_symbol, a_symbol, utc1_symbol, utc2_symbol, data_symbol, eos_symbol)
               
                    self.dsc_label.set(dsc_call)
                    self.dscqueue_off()
                    transmit_dsc(dsc_call, pwr) 
                    continue
                    #return
                    
                else:
                    a_symbol = mmsi_symbol(a_mmsi)
                    data_symbol = [ 126, 126, 126, 126, 126, 126 ]
        
            
        
            # if "All Ships" 
                if fmt_symbol == 116:
                    
            
                    if len(dfreq) > 12:
                        continue
                    data_symbol = freq_symbol(dfreq)
                    eos_e_symbol = eos_symbol
                    eos_symbol = 127
                    if (cat_symbol != 108) and (cat_symbol != 110) and (cat_symbol != 112):
                        cat_symbol = 108
                    
                    tc1_1_symbol = 100
                    
                    if (tc2_symbol != 126) and (tc2_symbol != 110) and (tc2_symbol != 111):
                        tc2_symbol = 126
                        
                    self.freq_var.set(True)
                    s_symbol = mmsi_symbol(s_mmsi)
                    self.dscqueue.put(0)
                    
                    dsc_call = build_call(fmt_symbol, a_symbol, cat_symbol, s_symbol, tc1_1_symbol, tc2_symbol, data_symbol, eos_symbol)

                    if (cat_symbol == 112) and (tc1_symbol == 110): # Distress Ack
                        pos_symbol = area_symbol(area)
                        a_symbol = mmsi_symbol(a_mmsi)
                        utc_sym = [ utc1_symbol, utc2_symbol ]
                        sub_symbol = 100
                        eos_symbol = 127
                        dsc_call = build_dis_ack_call(fmt_symbol, cat_symbol, s_symbol, tc1_symbol, a_symbol, msg1_symbol, pos_symbol, utc_sym, sub_symbol, eos_symbol)

                    if (cat_symbol == 112) and (tc1_symbol == 112): # Distress relays
                        pos_symbol = area_symbol(area)
                        a_symbol = mmsi_symbol(a_mmsi)
                        na_symbol = [ 126, 126, 126, 126, 126 ]
                        utc_sym = [ utc1_symbol, utc2_symbol ]
                        sub_symbol = 100
                        eos_symbol = 127
                        dsc_call = build_dis_ack_call(fmt_symbol, cat_symbol, s_symbol, tc1_symbol, a_symbol, msg1_symbol, pos_symbol, utc_sym, sub_symbol, eos_symbol)
               
                    self.dsc_label.set(dsc_call)
                    self.dscqueue_off()
                    transmit_dsc(dsc_call, pwr) 
                    continue
                # otherwise, set data to "no info" 
                else:
                    data_symbol = [ 126, 126, 126, 126, 126, 126 ]
                    
                    if (tc1_symbol == 121):
                        data_symbol = area_symbol(area)
                        
                        if (eos_symbol == 122):
                            data_symbol = data_symbol + [ utc1_symbol,  utc2_symbol ]
                        
                    if (tc1_symbol == 118):
                        data_symbol = [ 126 ]
            
                if (tc1_symbol == 109) or (tc1_symbol == 106) or (tc1_symbol == 113) or (tc1_symbol == 115) or (self.freq_var.get() == True):
                    if len(dfreq) > 12:
                        continue
                    self.freq_var.set(True)
                    data_symbol = freq_symbol(dfreq)
                    
                                 
            
                s_symbol = mmsi_symbol(s_mmsi)
                
                if (tc1_symbol == 121):
                    data_symbol = area_symbol(area) + [ 126, 126 ]
                    if (eos_symbol == 122):
                            data_symbol = area_symbol(area) + [ utc1_symbol,  utc2_symbol ]
        
                dsc_call = build_call(fmt_symbol, a_symbol, cat_symbol, s_symbol, tc1_symbol, tc2_symbol, data_symbol, eos_symbol)
               
                self.dsc_label.set(dsc_call)
                self.dscqueue_off()
                transmit_dsc(dsc_call, pwr) 
            #return
       

if __name__ == '__main__':
    root = Tk()
   
    root.geometry("670x750+10+10")
    root.title("VHF DSC " + version)
    root.resizable(1, 1)
    app = Application(root)
    
    
    root.mainloop()
