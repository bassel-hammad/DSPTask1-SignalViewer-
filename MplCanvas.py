import sys
import matplotlib
from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QFileDialog, QVBoxLayout,QHBoxLayout
import pandas as pd
import tkinter as tk
import math
matplotlib.use('Qt5Agg')
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.counter = 0
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        self.default_colors=["red","blue","yellow","green","brown","orange"]
        self.is_linked_with_canvas=False
        self.linked_canvas=self
        self.lst_colors=[]
        self.index_of_hidden_sig=[]
        self.dont_have_plots=True
        self.played=True
        self.lst_df = list()
        self.lst_df_names = []
        self.lst_df_colors = []
        self.lst_line = []
        self.lst_DataPlotted=[]
        self.time_label = None
        self.lst_ydata = []
        self.xdata=None
        self.timer =  QtCore.QTimer()
        self.axes.grid(True)
        self.window_size = 600  # Set the desired window size
        #self.window_size => determines the number of data points to be displayed on the plot.
        self.shift_amount = 5  # Set the number of data points to shift the window
        self.y_min = None
        self.y_max = None
        self.y_min_original = None
        self.y_max_original = None
        self.time_of_drawing =200
        self.zoomed_by=1.0

    def upload_data(self, df):
        self.lst_df.append(df) #The given DataFrame df is appended to the lst_df list,
        self.lst_df_names.append("")
        #select color for new data from default_colors
        self.lst_colors.append(self.default_colors[self.get_plots_number()-1 %len(self.default_colors) ])
        #set name =>in legend
        self.lst_df_names[self.get_plots_number()-1]="plot"+str(self.get_plots_number())
        #if there are no old  plots
        if(self.dont_have_plots):
            self.y_min = df.iloc[:, 1].min()
            self.y_max = df.iloc[:, 1].max()
            self.y_min_original = float(df.iloc[:, 1].min())
            self.y_max_original =  float(df.iloc[:, 1].max())
            self.time_label=df.iloc[:,0]
            self.axes.set_ylim(self.y_min, self.y_max)
            self.dont_have_plots=False
        # The initial window size is added to the lst_DataPlotted list. This list keeps track of the number of data points to be plotted, 
        self.lst_DataPlotted.append (self.window_size)  # Start with initial window of data
        self.lst_ydata=list(df.iloc[:,1])
        self.lst_line.append(None)
        self.update_data()
        self.update_canvas()
        self.timer = QtCore.QTimer()
        if(self.played):
            self.timer.timeout.connect(self.upgrade_canvas)
        self.timer.start(self.time_of_drawing)  # Update plot every 100 milliseconds

    def update_canvas(self): 
        # is responsible for updating the canvas with [(drawing)] the latest data 
        self.axes.clear()  #  Clears the current plot on the canvas.
        self.axes.grid(True)
        self.axes.set_facecolor('white')
        self.axes.set_ylim(self.y_min, self.y_max) #Sets the y-axis limits of the plot to the values stored in self.y_min and self.y_max.
        self.lst_line.clear()
        for i in range(len(self.lst_ydata)):
            if self.xdata is not None :
                #if  i in self.index_of_hidden_sig == True ,the user use add_to_hidden_lines function(i =index of plot) to hide it
                if( i in self.index_of_hidden_sig):
                    continue
                line,=self.axes.plot(self.xdata, self.lst_ydata[i], 'b')
                line.set_color(self.lst_colors[i])
                line.set_label(self.lst_df_names[i])
                self.axes.legend() 
                self.lst_line.append(line)
                # Hide x-axis labels
                #self.axes.set_xticklabels([])
        self.axes.set_autoscaley_on(False)  # Disable autoscaling of y-axis
        self.axes.set_autoscalex_on(True) 
        self.draw()

    def upgrade_canvas(self):
        self.axes.set_ylim(self.y_min, self.y_max)
        for i in range(len(self.lst_df)):
            if self.lst_DataPlotted[i] >= len(self.lst_df[i]):
                self.lst_DataPlotted[i]=self.window_size
            self.lst_DataPlotted[i]+= self.shift_amount
        self.update_data()
        #self.update_xlimits()
        self.update_canvas()
    #The update_data method is responsible for updating the y-data and time labels for each plot on the canvas.
    def update_data(self):
        self.axes.set_ylim(self.y_min, self.y_max)

        if(len(self.lst_DataPlotted)>0):
            self.xdata = self.time_label[self.lst_DataPlotted[0] - self.window_size:self.lst_DataPlotted[0]]
        self.lst_ydata.clear()
        for i in range(len(self.lst_df)):
            if(self.lst_DataPlotted[i]<self.window_size ) :
                continue
            #Slicing data frames
            ydata = self.lst_df[i].iloc[self.lst_DataPlotted [i] -self.window_size : self.lst_DataPlotted[i] , 1]
            self.lst_ydata.append(ydata)



    def zoom_in(self):
        self.y_min = self.y_min*0.9
        self.y_max = self.y_max*0.9
        self.window_size=int(self.window_size*0.95)
        self.zoomed_by=float(self.zoomed_by*0.9)
        if(self.is_linked_with_canvas):
            self.linked_canvas.zoom_in()
        self.update_data()
        #self.update_xlimits()
        self.update_canvas()

    def zoom_out(self):
        #self.window_size = int(self.window_size * 1.1)  # Increase window size by 10%
        self.y_min = self.y_min*1.1
        self.y_max = self.y_max*1.1
        self.window_size=int(self.window_size/0.95)
        self.zoomed_by=float(self.zoomed_by*1.1)
        if(self.is_linked_with_canvas):
            self.linked_canvas.zoom_out()
        self.update_data()
        #self.update_xlimits()
        self.update_canvas()

    def start_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.upgrade_canvas)
        self.timer.start(self.time_of_drawing)  # Update plot every 100 milliseconds

    def stop_timer(self):
        if self.timer is not None:
            self.timer.stop()
    
    def pause(self):
        if(self.is_linked_with_canvas):
            self.linked_canvas.pause()
        if(self.dont_have_plots):
            return
        self.stop_timer()
        self.played=False

    def play(self):
        if(self.is_linked_with_canvas):
            self.linked_canvas.play()
        if(self.dont_have_plots):
            return
        self.start_timer()
        self.played=True

    def pause_or_paly(self):
        if(self.played):
            self.pause()
        else:
            self.play()


    def increase_speed(self):
        if(self.is_linked_with_canvas):
            self.linked_canvas.increase_speed()
        self.time_of_drawing = float(self.time_of_drawing * 0.8)
        if(self.played):
            self.timer.start(self.time_of_drawing)

    def decrease_speed(self):
        if(self.is_linked_with_canvas):
            self.linked_canvas.decrease_speed()
        self.time_of_drawing=float(self.time_of_drawing*1.25)
        if(self.played):
            self.timer.start(self.time_of_drawing)


    def horizontal_scroll(self,shift_by):
        if(self.is_linked_with_canvas):
            self.linked_canvas.horizontal_scroll(shift_by)
        i=0
        for Data in self.lst_DataPlotted:
            if( Data + 50*shift_by >self.window_size):
                self.lst_DataPlotted[i]= Data + 50*shift_by
            i=i+1
        self.update_data()
        self.update_canvas()
    def vertical_scroll(self,i):
        if(self.is_linked_with_canvas):
            self.linked_canvas.vertical_scroll(i)

        self.y_min = self.zoomed_by*(self.y_min_original+(1/6)*i*abs(self.y_min_original))
        self.y_max = self.zoomed_by*(self.y_max_original+(1/6)*i*abs(self.y_max_original))
        self.update_data()
        #self.update_xlimits()
        self.update_canvas()
    def get_plots_number(self):
        return len(self.lst_df)
    
    
    def move_plot_from_canvas(self,i,canvas):
        if(len(self.lst_df)==0):
            return
        self.move_plot_to_another_canvas(self.lst_df[i],self.lst_DataPlotted[i],self.lst_colors[i],self.lst_df_names[i],self.time_label,canvas)
        self.remove_plot(i)
        self.update_canvas()

    def move_plot_to_another_canvas(self,df,data_plotted,color,name,time_label,canvas):
        canvas.upload_data(df)
        canvas.lst_DataPlotted[-1]=data_plotted
        canvas.lst_colors[-1]=color
        canvas.lst_df_names[-1]=name
        if(canvas.dont_have_plots):
            canvas.time_label=df.iloc[:,0]
        #canvas.update_canvas()

    def remove_plot(self,i):
        self.lst_df.pop(i)
        self.lst_DataPlotted.pop(i)
        self.lst_colors.pop(i)
        self.lst_df_names.pop(i)
        self.lst_ydata.pop(i)
        if(self.get_plots_number()==0):
            self.dont_have_plots=True
            self.lst_df.clear()
            self.lst_DataPlotted.clear()

    def rename_sig_from_canvas(self,i,newName):
        self.lst_df_names[i]=newName
        self.update_canvas()
    
    def change_color_of_siganl(self,i,the_color):
        self.lst_colors[i]=the_color
        #self.lst_line[i].set_color("black")
        if(not self.played):
            self.update_canvas()
        


    def add_to_hidden_lines(self,i):
        self.index_of_hidden_sig.append(i)

    def remove_from_hidden_line(self,i):
        if i in self.index_of_hidden_sig:
            self.index_of_hidden_sig.remove(i)
            return True
        else:
            return False
    def change_visibility(self,i):
        is_already_hidden=self.remove_from_hidden_line(i)
        if(not is_already_hidden ):
            self.add_to_hidden_lines(i)
        self.update_canvas()

    def link_canvas(self,canvas_2):
        self.is_linked_with_canvas=True
        canvas_2.is_linked_with_canvas=False
        self.linked_canvas=canvas_2
        #canvas_2.linked_canvas=self
        canvas_2.time_of_drawing=self.time_of_drawing
        canvas_2.timer.start(self.time_of_drawing)
        canvas_2.y_min=canvas_2.y_min_original+(self.y_min_original-self.y_min)
        canvas_2.y_max=canvas_2.y_max_original+(self.y_max_original-self.y_max)
        self.update_data()
        #self.update_xlimits()
        self.update_canvas()
    def rewind_signal(self,i):
        self.lst_DataPlotted[i]=self.window_size

    def get_statistics(self):
        statistics = []
        for i in range(len(self.lst_df)):
            statistics_1 = []
            statistics_1.append(str(self.lst_df_names[i]))
            statistics_1.append(f"{self.lst_ydata[i].mean():.4f}")
            statistics_1.append(f"{self.lst_ydata[i].std():.4f}")
            statistics_1.append(f"{self.lst_ydata[i].max():.4f}")
            statistics_1.append(f"{self.lst_ydata[i].min():.4f}")
            statistics.append(statistics_1)
            # If you want statistics for the DataFrame, not the current image
            # df.iloc[:,1] instead

        return statistics





