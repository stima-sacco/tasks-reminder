import wx
import wx.adv
import sqlite3
import wx.grid as gridlib
from datetime import datetime

conn = sqlite3.connect('my_database.db')

def execute_query(sql, query_type):
  response = None
  cursor = conn.cursor()

  if query_type == 'SELECT':
    response = cursor.execute(sql)
  elif query_type == 'INSERT':
    cursor.execute(sql)

  conn.commit()

  return response

def create_reminder_table():
  sql = '''
    CREATE TABLE IF NOT EXISTS reminders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reminder TEXT NOT NULL,
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
  '''
  
  response = execute_query(sql, 'INSERT')

ADD_BUTTON_ID = 1
SUBTRACT_BUTTON_ID = 2

class MyGrid(gridlib.Grid):
    def __init__(self, parent):
        super().__init__(parent, pos=(10, 150), size=(550, 100))

        # Create a 10x3 grid initially
        self.CreateGrid(0, 4)
        self.set_column_labels()
        # Set custom colors for alternating rows
        self.set_row_colors()

    def set_column_labels(self):
            # Set the labels for each column
            column_labels = ["Id", "Reminder", "Due Date", "Created Date"]
            for col, label in enumerate(column_labels):
                self.SetColLabelValue(col, label)

    def set_row_colors(self):
        # Loop through rows and alternate background colors
        for row in range(self.GetNumberRows()):
            if row % 2 == 0:
                self.set_row_background(row, wx.Colour(230, 230, 255))  # Light blue
            else:
                self.set_row_background(row, wx.Colour(255, 255, 255))  # White

    def set_row_background(self, row, color):
        # Apply background color to all cells in the row
        for col in range(self.GetNumberCols()):
            self.SetCellBackgroundColour(row, col, color)
        self.ForceRefresh()

    def clear_grid(self):
        # Clear all rows from the grid
        self.DeleteRows(0, self.GetNumberRows())

    def add_new_row(self, values):
        # Add one new row to the grid
        self.AppendRows(1)

        # Get the total number of rows and set color for the new row
        row = self.GetNumberRows() - 1  # Index of the last row
        
        for col, value in enumerate(values):
            self.SetCellValue(row, col, str(value))

        # Set the new row's background color based on its position
        if row % 2 == 0:
            self.set_row_background(row, wx.Colour(230, 230, 255))  # Light blue
        else:
            self.set_row_background(row, wx.Colour(255, 255, 255))  # White

class Form(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='Reminder', size=(600,400))
        self.Pan = wx.Panel(self, -1)

        self.streminder = wx.StaticText(self.Pan, label='Reminder', pos=(10, 40), size=(70, 20))
        self.tcReminder = wx.TextCtrl(self.Pan, pos=(80, 40), size=(70, 20))

        self.stdue_date = wx.StaticText(self.Pan, label='Due Date', pos=(10, 70), size=(70, 20))
        self.due_date = wx.adv.DatePickerCtrl(self.Pan, pos=(80, 70), size=(130, 20), style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)

        self.reminder_grid = MyGrid(self.Pan)
        self.btnStore = wx.Button(self.Pan, id=ADD_BUTTON_ID, label='Store', pos=(10, 130), size=(50,20))
        self.btnStore.Bind(wx.EVT_BUTTON, self.Evt_Store) #subscribe to the event
        
        self.Pan.Bind(wx.EVT_SIZE, self.Evt_Resize)

        self.display_reminders_on_grid()

    def display_reminders_on_grid(self):
        sql = 'SELECT * FROM reminders'

        response = execute_query(sql, 'SELECT')

        row_counter = 0
        for row in response.fetchall():
            self.reminder_grid.add_new_row(row)
            days_to_due_date = self.get_days_to_due_date(row[2])

            if days_to_due_date <= 10:
                self.reminder_grid.set_row_background(row_counter, wx.Colour(255, 0, 0))
            elif days_to_due_date <= 20:
                self.reminder_grid.set_row_background(row_counter, wx.Colour(50, 205, 50))
            elif days_to_due_date <= 30:
                self.reminder_grid.set_row_background(row_counter, wx.Colour(238, 130, 238))
            else:
              self.reminder_grid.set_row_background(row_counter, wx.Colour(255, 255, 255))
            row_counter += 1

    def get_days_to_due_date(self, due_date):
      dtDueDate = datetime.strptime(due_date, "%Y-%m-%d").date()
      today = datetime.now().date()

      difference = dtDueDate - today
      return difference.days

    def Evt_Store(self, evt):
        nButtonId = evt.GetId()

        reminder = self.tcReminder.Value
        due_date = self.due_date.Value

        date_str = due_date.FormatISODate()

        sql = """INSERT INTO reminders (reminder, due_date)
        VALUES ('""" + reminder + """','""" + date_str + """')"""
        
        execute_query(sql, 'INSERT')

        self.reminder_grid.clear_grid()
        self.display_reminders_on_grid()

    def Addition(self):
        try:
            num1 = int(self.tcReminder.Value)
            num2 = int(self.tcNumber2.Value)

            self.tcResult.Value = str(num1 + num2)
        except Exception as err:
            wx.MessageBox(str(err))

    def Subtraction(self):
        try:
            num1 = int(self.tcReminder.Value)
            num2 = int(self.tcNumber2.Value)

            self.tcResult.Value = str(num1 - num2)
        except Exception as err:
            wx.MessageBox(str(err))

    def Evt_Resize(self, evt):
        nHeight = self.GetSize()[1]
        nWidth = self.GetSize()[0]
        
        self.btnStore.SetPosition((10, (nHeight -60)))
        self.reminder_grid.SetPosition((10, 150))
        
        self.reminder_grid.SetSize(((nWidth - 70), (nHeight - 250)))

if __name__ == '__main__':
    app = wx.App()
    create_reminder_table()
    Form().Show()
    app.MainLoop()        