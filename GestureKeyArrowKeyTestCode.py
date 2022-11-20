# Import the Required libraries
from tkinter import *

# Create an instance of tkinter frame or window
win = Tk()

agent_next_data = 'Improving Efficiency and Robustness of Transformer-based \n Information Retrieval Systems....'
agent_last_data = 'new window'
agent_new_data = 'New Window New Data'
idle_state = 'Loading...'
# Set the size of the window
win.geometry("700x350")


# Define a function to display the messages
def key_press(e):
    label.config(text=agent_new_data)


def key_released(e):
    label.config(text=idle_state)


def left_arrow(e):
    label.config(text=agent_new_data)


def right_arrow(e):
    label.config(text=agent_new_data)


def up_arrow(e):
    label.config(text=agent_next_data)


def down_arrow(e):
    label.config(text=agent_next_data)


# attempt @ getting updates In progress


# Create a label widget to add some text
label = Label(win, text="", font='Helvetica 17 bold')
label.pack(pady=100)
win.title("Data Stream")

#bind arrow keys
win.bind('<KeyRelease>',key_released)
win.bind('<Left>', left_arrow)
win.bind('<Right>', right_arrow)
win.bind('<Up>', up_arrow)
win.bind('<Down>', down_arrow)

win.mainloop()
