import wx, wx.grid as grd  
from logging import exception
import ConfigParser
import sqlite3
import csv

selected_tables = set()
selected = set()

class DbCon():
    def __init__(self):
        config = ConfigParser.ConfigParser()
        configFilePath = r'config.ini'
        config.read(configFilePath)
        self.adr = config.get("db", "address")
        self.prt = config.get("db", "port")
        self.usr = config.get("db", "user")
        self.pwd = config.get("db", "password")
        self.pdb = config.get("db", "db")
        self.table_list = []

        try:
            connection = sqlite3.connect("test.db")
            cursor = connection.cursor()
            cursor.execute("select tbl_name from sqlite_master")
            rows = cursor.fetchall()
            for r in rows:
                self.table_list.append(r[0])
        except exception as ex:
            print(ex)
        finally:
            if connection:
                connection.close()
    
    def csvwrite(self, data):
        global selected
        for tbl in selected_tables:
            td = self.query(tbl)
        
            with open(tbl + ".csv", "w") as csvfile:
                table = csv.writer(csvfile)
                for c in td:
                    table.writerow(c)
        
    
    def query(self, table):
        try:
            connection = sqlite3.connect("test.db")
            cursor = connection.cursor()
            cursor.execute("select * from %s" % table)
            rows = cursor.fetchall()
            
        except exception as ex:
            print(ex)
            rows = None
        
        finally:
            if connection:
                connection.close()
            return rows


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title =title, size = (800,600))
 
        button = wx.Button(self, wx.ID_ANY, 'Save', (700, 500))
        button.Bind(wx.EVT_BUTTON, d.csvwrite)
 
        self.panel = MyGrid(self)
        

class MyGrid(grd.Grid):
    def __init__(self, parent):
        grd.Grid.__init__(self, parent, -1, pos=(10,40), size=(420, 95))
 
        global selected_tables
        global selected
        
        i = 0
        
        r = len(d.table_list)
        
        self.CreateGrid(r,2)
        self.RowLabelSize = 0
        self.ColLabelSize = 20
        attr = grd.GridCellAttr()
        attr.SetEditor(grd.GridCellBoolEditor())
        attr.SetRenderer(grd.GridCellBoolRenderer())
        self.SetColAttr(0,attr)
        self.SetColSize(0,20)

        if len(d.table_list) != 0:
            for t in d.table_list:
                self.SetCellValue(i, 1, str(t))
                i += 1

        self.Bind(grd.EVT_GRID_CELL_LEFT_CLICK,self.onMouse)
        self.Bind(grd.EVT_GRID_SELECT_CELL,self.onCellSelected)
        self.Bind(grd.EVT_GRID_EDITOR_CREATED, self.onEditorCreated)
   
    def onMouse(self,evt):
        if evt.Col == 0:
            
            if evt.Row not in selected:
                selected.add(evt.Row)
                
                selected_tables.add(self.GetCellValue(evt.Row, 1))
                
            else:
                selected.remove(evt.Row)
                
                selected_tables.remove(self.GetCellValue(evt.Row, 1))
                
            wx.CallLater(0,self.toggleCheckBox)
            evt.Skip()

    def toggleCheckBox(self):
           self.cb.Value = not self.cb.Value
           self.afterCheckBox(self.cb.Value)
   
    def onCellSelected(self,evt):
           if evt.Col == 0:
               wx.CallAfter(self.EnableCellEditControl)
           evt.Skip()
   
    def onEditorCreated(self,evt):
           if evt.Col == 0:
               self.cb = evt.Control
               self.cb.WindowStyle |= wx.WANTS_CHARS
               self.cb.Bind(wx.EVT_KEY_DOWN,self.onKeyDown)
               self.cb.Bind(wx.EVT_CHECKBOX,self.onCheckBox)
               evt.Skip()
   
    def onKeyDown(self,evt):
            if evt.KeyCode == wx.WXK_UP:
                if self.GridCursorRow > 0:
                    self.DisableCellEditControl()
                    self.MoveCursorUp(False)
            elif evt.KeyCode == wx.WXK_DOWN:
                if self.GridCursorRow < (self.NumberRows-1):
                   self.DisableCellEditControl()
                   self.MoveCursorDown(False)
            elif evt.KeyCode == wx.WXK_LEFT:
                if self.GridCursorCol > 0:
                   self.DisableCellEditControl()
                   self.MoveCursorLeft(False)
            elif evt.KeyCode == wx.WXK_RIGHT:
                if self.GridCursorCol < (self.NumberCols-1):
                   self.DisableCellEditControl()
                   self.MoveCursorRight(False)
            else:
                evt.Skip()
   
    def onCheckBox(self,evt):
           self.afterCheckBox(evt.IsChecked())
   
    def afterCheckBox(self,isChecked):
        self.GridCursorRow,isChecked
        if self.GridCursorRow == isChecked:
            print(self.GridCursorRow)
      

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(parent=None, title="Database converter")
        self.frame.Show()
        return True
 
d = DbCon()
app = MyApp()
app.MainLoop()
