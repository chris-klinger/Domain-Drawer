#!/usr/bin/env python

import sys
import os
import re

import Tkinter
from tkFont import Font

class Plot:

    # unscaled space around the canvas
    canvas_pad_x = canvas_pad_y = canvas_border = 0
    x_margin = y_margin = 20
    x_axis_width = 3
    y_axis_width = 0
    x_axis_font_size = y_axis_font_size = 12
    x_tic_length = y_tic_length = 3
    x_tic_width = y_tic_width = 1
    canvas_background = 'white'
    proteinwidth = 15
    proteinspacing = 15

    serif_faces = ('Palatino', 'Georgia', 'Times')
    sans_faces = ('Futura', 'Gill Sans', 'Verdana', 'Helvetica', 'Arial')
    mono_faces = ('Liberation Mono Regular',
                  'Lucida Sans Typerwriter',
                  'DejaVu Sans Mono',
                  'Bitstream Sans Mono',
                  'Courier')

    Instances = []
    PlotNumber = 0

## Utility Class Methods

    @classmethod
    def file_name_only(self, path):
        return os.path.splitext(os.path.split(path)[1])[0]

    @classmethod
    def NextPlotNumber(self):
        self.PlotNumber += 1
        return str(self.PlotNumber)

    @classmethod
    def closeall(self):
        for inst in self.Instances:
            inst.close()

## Utility Instance Methods

    def findfont(self, faces, sz=11, boldflg=False, italicflg=False):
        for face in faces:
            font = Font(root=self.root,
                        family=face,
                        size=sz,
                        weight = 'bold' if boldflg else 'normal',
                        slant = 'italic' if italicflg else 'roman')
            if face == font.actual('family'):
                return font

# Access
    def get_root(self):
        return self.root

    def add_font(self, name, font):
        self.fonts[name] = font

    def get_font(self, name):
        return self.fonts.get(name, None)

## Fundamental methods

    def __init__(self, maxlength, data, colors, spacing, windowtitle=None,
                 scale=1.0, ps_filename=None, ps_scale = 1.0):
        self.Instances.append(self)
        self.fonts = {}
        self.window_title = (windowtitle or
                             self.PlotName + ' ' + self.NextPlotNumber())
        self.root = Tkinter.Tk()
        self.root.title(self.window_title)

        self.scale = scale
        self.ps_filename = ps_filename
        self.ps_scale = ps_scale

        self.data = data
        self.maxlength = maxlength
        self.spacing = spacing
        self.colors = colors
#        print self.colors

        self.setup()

    def __str__(self):
        return self.window_title

## Layout Framework

    def setup(self):
        self.setup_fonts()
        self.setup_data()
        self.setup_parameters()
        (self.plot_width, self.plot_height,
         self.plot_left_margin, self.plot_right_margin,
         self.plot_top_margin, self.plot_bottom_margin) = \
            self.get_plot_dimensions()
        self.determine_layout()

    def setup_fonts(self):
        self.add_font('x', self.findfont(self.sans_faces,
                                         self.x_axis_font_size,
                                           True))
        self.add_font('y', self.findfont(self.sans_faces,
                                         self.y_axis_font_size,
                                         True))

#    def setup_fonts(self):
#        self.add_font('x', self.findfont(self.codon_faces,
#                                         self.codon_font_size,
#                                         True))
#        self.add_font('title',self.findfont(self.sans_faces,
#                                            self.key_font_size,
#                                            True))

#    def setup_data(self):
#        pass

    def setup_data(self):
        self.IDs = self.data.keys()
        self.numkeys = len(self.IDs)
#        self.Info = self.data.get(self.IDs)
#        self.maxval = max(self.data.values())
#        self.sumval = sum(self.data.values())
#        self.maxpercent = round((100 * self.maxval) / self.sumval)

    def setup_parameters(self):
        pass

#    def get_plot_dimensions(self):
#        """Return a tuple of six values describing the placement and
#        dimensions of the plot within the canvas:
#        (plot_width, plot_height, left_margin, right_margin,
#         top_margin, bottom_margin)"""
#        raise SubclassResponsibility(
#            "Subclass must implement get_plot_dimensions")

    def get_plot_dimensions(self):
        return (self.scale * int(self.maxlength),
               self.scale * (round(self.numkeys * (self.proteinwidth +
                                                   self.proteinspacing))),
               (4 * self.x_margin),
               self.x_margin,
               self.y_margin,
               self.y_margin
               )

    def determine_layout(self):
        self.origin_x = self.plot_left_margin + self.y_axis_width
        self.origin_y = self.plot_top_margin + self.plot_height
        self.canvas_width = (self.plot_left_margin +
                             self.y_axis_width +
                             self.plot_width +
                             self.plot_right_margin)
        self.canvas_height = (self.plot_top_margin +
                              self.plot_height +
                              self.x_axis_width +
                              self.plot_bottom_margin)

## Drawing Framework

    def execute(self):
        self.create_widgets()
        self.draw_axes()
        if self.ps_filename:
            self.write_postscript()
        return self

    def close(self):
        if self in self.Instances:
            self.Instances.remove(self)
        if self.root:
            self.root.destroy()

    def create_widgets(self):
        self.create_canvas()

    def create_canvas(self):
        self.canvas = Tkinter.Canvas(self.root,
                                     width=self.canvas_width,
                                     height=self.canvas_height,
                                     bd=self.canvas_border,
                                     bg=self.canvas_background)
        self.canvas.pack(side='top',
                         padx=self.canvas_pad_x,
                         pady=self.canvas_pad_y)

    def draw_axes(self):
        xadjust = round(self.x_axis_width / 2)
        yadjust = round(self.y_axis_width  / 2)
        if self.x_axis_width:
            self.draw_line(-xadjust, -yadjust,
                           self.plot_width - xadjust, -yadjust,
                           self.x_axis_width)
#            self.draw_x_axis_labels()
        if self.y_axis_width:
            self.draw_line(-xadjust, -yadjust,
                           -xadjust, self.plot_height - yadjust,
                           self.y_axis_width)
        self.draw_y_axis()
        self.draw_x_tics()
#        self.draw_y_tics()

    def draw_x_tics(self):
        num_chunks = int(self.maxlength)/int(self.spacing)
        for i in range(1, num_chunks):
            self.draw_line((i * 50), 0, (i * 50), -self.x_tic_length, self.x_tic_width)
            self.draw_text((i * 50), -(5 * self.x_tic_length), ("%s" % (i * 50)), 'x')

    def draw_y_tics(self):
        pass
#
#    def draw_x_axis_labels(self):
#        pass
#
    def draw_y_axis(self):
        cury = self.canvas_height - (self.proteinspacing + self.proteinwidth + 10)
        n = 0
        while n < self.numkeys:
            self.draw_protein_label(cury, self.IDs[n])
            self.draw_plot(cury, self.IDs[n])
            cury -= (self.proteinwidth + self.proteinspacing)
            n += 1
#
    # y below is a reference to cury
    #implement some scheme for drawing labels
    def draw_protein_label(self, y, key):
        self.draw_text(-(self.plot_left_margin - 5),
                        y,
                        key,
                        'y',
                        anchor='w')
#
##    def draw_plot(self):
##        raise SubclassResponsibility(
##            "Subclass must implement draw_plot")
#
    # implement a scheme for drawing the actual domains
    def draw_plot(self, y, key):
        self.draw_line(0,y,int((self.data[key][0][0])),y,2)
        n = self.enum(key)
#        print n
        for v in range (1, (n+1)):
            try:
#                print v
#                print self.data[key][v]
                S = int(self.data[key][v][0])
                E = int(self.data[key][v][1])
                T = self.data[key][v][2]
                print S
                print E
                print T
                self.draw_oval(S,y-5,E,y+5,width=0,fill=self.colors[T])
            except(IndexError):
                pass

    def enum(self, key):
        dict = self.data
        n=0
        try:
            while dict[key][n][0]:
                n+=1
        except(IndexError):
            pass
        return n

#
    def write_postscript(self):
        self.canvas.postscript(
            file=self.ps_filename,
            width=self.canvas_width,
            height=self.canvas_height,
            pagewidth=self.ps_scale*self.canvas_width,
            colormode='color')
#        print 'wrote', self.ps_filename, file=sys.stderr


## Drawing functions
## y=0 at canvas x-axis, not top

    def draw_line(self, x1, y1, x2, y2, width=1, fill='black'):
        """Draw line on canvas relative to canvas origin and scale"""
        self.canvas.create_line(self.origin_x + round(x1*self.scale),
                                self.origin_y - round(y1*self.scale),
                                self.origin_x + round(x2*self.scale),
                                self.origin_y - round(y2*self.scale),
                                width=round(width*self.scale),
                                fill=fill,
                                capstyle='projecting',
                                )

    def draw_line_unscaled(self, x1, y1, x2, y2, width=1, fill='black'):
        """Draw line on canvas in unscaled coordinates, unscaled"""
        self.canvas.create_line(self.origin_x + x1,
                                self.origin_y - y1,
                                self.origin_x + x2,
                                self.origin_y - y2,
                                width=width,
                                fill=fill,
                                )

    def draw_oval(self, x1, y1, x2, y2, width=1, fill='black'):
        """Draw oval on canvas relative to canvas origin and scale"""
        self.canvas.create_oval(self.origin_x + round(x1*self.scale),
                                self.origin_y - round(y1*self.scale),
                                self.origin_x + round(x2*self.scale),
                                self.origin_y - round(y2*self.scale),
                                width=round(width*self.scale),
                                fill=fill,
                                )

    def draw_rectangle(self, x, y, w, h, fill='black'):
        """Draw rectangle on canvas relative to canvas origin and scale"""
        x = self.origin_x + x*self.scale
        y = self.origin_y - y*self.scale
        self.canvas.create_rectangle(x, y, x+w, y-h, fill=fill)

    def draw_text(self, x, y, txt, fontname,
                  anchor='center', fill='black'):
        """Draw text on canvas relative to canvas origin and scale"""
        self.canvas.create_text(
                self.origin_x + round(x*self.scale),
                self.origin_y - round(y*self.scale),
                text=txt,
                font=self.get_font(fontname),
                anchor=anchor,
                fill=fill,
                )

    def draw_text_unscaled(self, x1, y1, txt, fontname,
                           anchor, fill='black'):
        self.canvas.create_text(x1, y1, text=txt,
                                font=self.get_font(fontname),
                                anchor=anchor, fill=fill,
                                )


    def describe_font(self, name):
        font = self.get_font(name)
        print(font.actual('family'),
              font.actual('size'),
              font.actual('weight'),
              font.actual('slant')
              )

    def describe_fonts(self):
        for k in sorted(self.fonts.keys()):
#            print '{:12}'.format(k), end='\t'
            self.describe_font(k)

    def show(self):
        descr(self)


TestDict = {'33066':[['400'],['122','347','PF00566.13','RabGAP-TBC']],
'76746':[['420'],['275','346','PF00566.13','RabGAP-TBC']],
'142360':[['300'],['59','144','PF00566.13','RabGAP-TBC'], ['165','230','PF00612.13','OtherDomain']]}

ColorDict = {'PF00566.13':'gray80','PF00612.13':'blue'}

def find_max_value(dict):
	maxvalue = ''
	for k in dict.keys():
		v1 = dict[k][0][0]
		if v1 > maxvalue:
			maxvalue = v1
		else:
			pass
	return maxvalue

maxval = find_max_value(TestDict)

Test = Plot(maxval, TestDict, ColorDict, 50, "TestCanvas", ps_filename="Test.ps")
Test.execute()
input('Press the Return key to close the window(s)')
Test.close
