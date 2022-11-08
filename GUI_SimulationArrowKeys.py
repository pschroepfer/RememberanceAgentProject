


#displays information in window to test on UI and to practice time intervals



#import tkinter as tk

#window = tk.Tk()

#frame_a = tk.Frame()

#label_a = tk.Label(master=frame_a, text="Ubiquitus computing Live Remembrance Agent Stream ")
#label_a.pack()
#window.title("Remembrance Agent")
#frame_b = tk.Frame()
#label_b = tk.Label(master=frame_b, text="PDF TRANSCRIPTS RELAYED HERE FOR PROCESSING")
#label_b.pack()

#Swap the order of `frame_a` and `frame_b`
#frame_b.pack()
#frame_a.pack()

#window.mainloop()



from tkinter import *
import time
import threading

def calculation_task():
    print("started")
    # simulate calculation
    time.sleep(5)
    print("completed")
    # task completed, notify main task via virtual event
    window.event_generate("<<Complete>>", when="tail")

def on_complete(event):
    msg2 = Label(window, text="REMEMBRANCE AGENT INFORMATION TO DISPLAY INTERVAL TESTING")
    msg2.pack()





window = Tk()
window.geometry("700x700")
window.title("Remembrance Agent")
msg1 = Label(window, text="AGENT INFORMATION TO DISPLAY INTERVAL TEST")
msg1.pack()



# bind virtal event
window.bind("<<Complete>>", on_complete)
# start calculation task in other thread
threading.Thread(target=calculation_task).start()



window.mainloop()


#ARROW KEY???

#my_w.bind('<Right>',right)
#my_w.bind('<Left>',left)
#my_w.bind('<Up>',up)
#my_w.bind('<Down>',down)

#my_w.bind("<Right>",lambda e:l1.config(text='Right arrow'))

