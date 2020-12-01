from collections import namedtuple
from random import randint, random
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QPainter, QPicture
from PyQt5.QtWidgets import QApplication
from pyqtgraph import PlotWidget, plot, QtCore
import pyqtgraph as pg
import sys
from numpy import array, zeros, ndenumerate, transpose
from Defines import *


# shapes from: github.com/abhilb/pyqtgraphutils/blob/master/pyqtgraphutils.py
class CircleItem(pg.GraphicsObject):
    def __init__(self, center, radius):
        pg.GraphicsObject.__init__(self)
        self.center = center
        self.radius = radius
        self.generatePicture()

    def generatePicture(self):
        self.picture = QPicture()
        p = QPainter(self.picture)
        p.setPen(pg.mkPen('k'))
        p.drawEllipse(self.center[0], self.center[1], self.radius * 2, self.radius * 2)
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())

class RectangleItem(pg.GraphicsObject):
    def __init__(self, topLeft, size):
        pg.GraphicsObject.__init__(self)
        self.topLeft = topLeft
        self.size = size
        self.generatePicture()

    def generatePicture(self):
        self.picture = QPicture()
        p = QPainter(self.picture)
        p.setPen(pg.mkPen('k'))
        tl = QtCore.QPointF(self.topLeft[0], self.topLeft[1])
        size = QtCore.QSizeF(self.size[0], self.size[1])
        p.drawRect(QtCore.QRectF(tl, size))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())
    #
#

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.graphWidget.setXRange(0, 100)
        self.graphWidget.setYRange(0, 100)
        self.graphWidget.setBackground('w')
        self.graphWidget.getPlotItem().hideAxis('bottom')
        self.graphWidget.getPlotItem().hideAxis('left')
        self.font = QFont()

        self.font_size = 15
        self.dot_size = 10
        self.bridge_size = 5
        self.label_offset = self.dot_size / 4
        self.label_height = self.font_size / 6
        self.bridge_line = pg.mkPen(color=(0, 0, 0), width=1.5, style=QtCore.Qt.SolidLine)

        self.font.setPixelSize(self.font_size)


        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
    #

    # Plot black point and annotation text
    # x, y => coords, name => name of the point, index => index of name,
    # side => is point name on left (0) or right (1)
    def plot_point(self, x, y, name, index, side):
        if not side:
            t_up.setPos(x - 1, y - self.font_size / 6)
        else:
            t_up.setPos(x + dot_size/2, y - self.font_size / 6)
        t_up.setFont(self.font)

        self.graphWidget.addItem(t_up)
    #

    # Plot circle with symbol inside, representing specific sum
    # Firstly, correct coords by the radius size
    def plot_sum(self, x, y, name, index, radius):
        x, y = x - radius, y - radius
        c1 = CircleItem([x, y], radius)

        # Add text label to sum
        t_up = pg.TextItem(html=name + f"<sub>{index}</sub>", anchor=(1, 1))
        # self.graphWidget.plot([x], [y+radius], symbol='o', symbolSize=10, symbolBrush="k")
        t_up.setPos(x + 4.5, y)
        t_up.setFont(self.font)
        #

        self.graphWidget.addItem(c1)
        self.graphWidget.addItem(t_up)
    #

    # Plot halamards sum
    def plot_h(self, x, y, x_size, y_size):
        c1 = RectangleItem([x, y], [x_size, y_size])
        name = "H"
        index = 2

        # Add text label to h
        t_up = pg.TextItem(html=f"<b>{name}</b>" + f"<sub>{index}</sub>", anchor=(1, 1))
        t_up.setPos(x + x_size * 0.9, y + y_size / 3.5)
        t_up.setFont(self.font)
        #

        # todo: add 4 points, 2 on each side of the square

        self.graphWidget.addItem(c1)
        self.graphWidget.addItem(t_up)
    #

    # connect two points with a line
    # p_s is tuple with start coordinates (x, y)
    # p_e is a tuple with end coordinates (x, y)
    def plot_connect_points(self, p_s, p_e, line_type=1):
        ln_obj = 0
        if line_type == 1:
            ln_obj = QtCore.Qt.SolidLine
        elif line_type == -1:
            ln_obj = QtCore.Qt.DashLine

        line = pg.mkPen(color=(0, 0, 0), width=1.5, style=ln_obj)
        self.graphWidget.plot([p_s.x, p_e.x], [p_s.y, p_e.y], pen=line, symbol='o', symbolSize=10, symbolBrush="k")
    #

    # Function deciding whether specific point has junction connections (returns True) or just one simple
    # connection to another point in the same "row" (returns False)
    # mx => matrix that will be checked
    # i  => index to check
    # column => True, check column || False, check row
    def check_junction(self, mx, index, column):
        not_junction = True # by default, point does not have junction
        if column:
            for i, el in ndenumerate(transpose(mx)[index]):
                if el != 0 and i[0] != index:
                    not_junction = False
        else:
            for i, el in ndenumerate(mx[index]):
                if el != 0 and i[0] != index:
                    not_junction = False
        return not_junction
    #

    # in case there is junction, bridge must be plotted to extend point's arm
    # x, y is just point coords
    # size is the length of arm
    # dir 1 => left, 0 => right (direction of point's arm/bridge)
    # returns => coords of the end of bridge, will be the new point
    def plot_bridge(self, bridge, label="", index=0):

        if label != "":
            label_item = pg.TextItem(html=label + f"<sub>{index}</sub>", anchor=(1, 1))

            if bridge.bridge_side() == BRIDGE_LEFT:
                label_side = LABEL_RIGHT
            else:
                label_side = LABEL_LEFT

            if label_side == LABEL_LEFT:
                label_item.setPos(bridge.left_point.x - self.label_offset, bridge.left_point.y - self.label_height)
            elif label_side == LABEL_RIGHT:
                label_item.setPos(bridge.right_point.x + self.bridge_size + self.label_offset, bridge.right_point.y - self.label_height)
            label_item.setFont(self.font)
            self.graphWidget.addItem(label_item)

        self.graphWidget.plot([bridge.left_point.x], [bridge.left_point.y], symbol='o', symbolSize=self.dot_size, symbolBrush="k")
        self.graphWidget.plot([bridge.left_point.x, bridge.right_point.x], [bridge.left_point.y, bridge.right_point.y], pen=self.bridge_line)
        self.graphWidget.plot([bridge.right_point.x], [bridge.right_point.y], symbol='o', symbolSize=self.dot_size, symbolBrush="k")
        return Point.fromPoint(bridge.right_point)
    #

    # Given set of input points m_in, output points m_out and x_s, y_s as starting coords
    def plot_scheme(self, m_in, m_out, sum_labels, x_s, y_s):
        # space between columns in graph
        x_offset = 30
        # coords of specific points and sums
        # x coordinates
        m_in_cds  = []
        # coordinates of points on the left of sum
        m_sum_cds_l = []
        # coordinates of points on the right of sum
        m_sum_cds_r = []



        # y coordinates
        new_col_cds  = []
        next_col_cds = []
        mx_list      = [m_in, m_out]
        #

        # -----------------------------------
        # phase 1 - plot all points
        # plot starting point
        # start point for drawing graph
        start_bridge  = Bridge(Point(x_s, y_s), length=self.bridge_size)
        point_height_offset = - 10

        for pt_nr in range(mx_list[0].shape[1]):
            sp = self.plot_bridge(start_bridge, "x", index=pt_nr)

            if pt_nr == 0:
                y_offset = 0
                for i in range(mx_list[0].shape[0]):
                    next_bridge = Bridge(sp + Point(x_offset, y_offset), length=self.bridge_size)
                    self.plot_bridge(next_bridge)
                    new_col_cds  += [next_bridge.left_point]
                    next_col_cds += [next_bridge.right_point]
                    y_offset -= 10
            #
            for coord in range(mx_list[0].shape[0]):
                self.plot_connect_points(sp, new_col_cds[coord], line_type=mx_list[0][coord][pt_nr])

            start_bridge += Point(0, point_height_offset)
        #




        # plot input (x)i points
        # y_offset = 0
        # for i in range(m_in.shape[0]):
        #     self.plot_point(x_s, y_s + y_offset, "x", i, 0)
        #     new_point = self.plot_bridge(x_s, y_s + y_offset, 5)
        #     m_in_cds += [new_point]
        #     y_offset -= 10

        # plot sum (s)i circles
        # y_offset = 0
        # for s in range(m_in.shape[1]):
        #     self.plot_sum(x_s + x_offset, y_s + y_offset, *sum_labels[s], 3)
        #     m_sum_cds_l += [(x_s + x_offset - 3, y_s + y_offset)]
        #     m_sum_cds_r += [(x_s + x_offset + 3, y_s + y_offset)]
        #     y_offset -= 10
        #
        #
        # # plot output (y)i points
        # y_offset = 0
        # for i in range(m_out.shape[1]):
        #     self.plot_point(x_s + 2 * x_offset, y_s + y_offset, "y", i, 1)
        #     new_point = self.plot_bridge(x_s + 2 * x_offset, y_s + y_offset, -5)
        #     m_out_cds += [new_point]
        #     y_offset -= 10


        # -----------------------------------
        # phase 2 - connect points and sums
        # connect input points and sums
        # for cds, val in ndenumerate(m_in):
        #     self.plot_connect_points(m_in_cds[cds[0]], m_sum_cds_l[cds[1]], val)
        #
        # # connect output points and sums
        # for cds, val in ndenumerate(m_out):
        #     self.plot_connect_points(m_sum_cds_r[cds[0]], m_out_cds[cds[1]], val)
    #


def get_scheme_1():
    m_in = array([[1, 1, 0], [1, 0, 1]])
    m_out = array([[1, 0], [0, 1], [0, 1]])
    sum_labels = [("a", ""), ("b", ""), ("c", "")]
    return m_in, m_out, sum_labels

def get_scheme_4():
    m_in = array([[1, 0, -1], [0, 1, 1]])
    m_out = array([[0, 1], [1, 0], [1, 1]])
    sum_labels = [("φ", 0), ("φ", 1), ("a", "")]
    return m_in, m_out, sum_labels


def main():
    # Special symbols: φ  ŝ
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()

    m_in, m_out, sum_labels = get_scheme_4()


    main.plot_scheme(m_in, m_out, sum_labels, 20, 60)

    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()