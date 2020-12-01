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
        # Offset for next bridges to be placed below on a specific column
        self.point_height_offset = -10
        # space between columns in graph
        self.x_offset = 30
        self.x_s = 20
        self.y_s = 60

        self.font.setPixelSize(self.font_size)


        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
    #

    # Plot black point and annotation text
    # x, y => coords, name => name of the point, index => index of name,
    # side => is point name on left (0) or right (1)
    # def plot_point(self, x, y, name, index, side):
    #     if not side:
    #         t_up.setPos(x - 1, y - self.font_size / 6)
    #     else:
    #         t_up.setPos(x + dot_size/2, y - self.font_size / 6)
    #     t_up.setFont(self.font)
    #
    #     self.graphWidget.addItem(t_up)
    # #

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
    def plot_bridge(self, bridge, label="", index=0, label_side=LABEL_LEFT):
        if label != "":
            label_item = pg.TextItem(html=label + f"<sub>{index}</sub>", anchor=(1, 1))

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
    def plot_scheme(self, mx_list):
        # Create starting point
        start_bridge  = Bridge(Point(self.x_s, self.y_s), length=self.bridge_size)

        # First, draw second column, that input (x) column will connect to
        # Save all coordinates of bridges in a new_bridges list
        new_bridges = list(self.set_bridges(mx_list[0].shape[1], start_bridge))

        # Secondly, iterate over input (x) points and connect each of them with specific
        # bridge they should be connected to
        # Iterate over rows (inputs)
        for pt_nr in range(mx_list[0].shape[0]):
            # Plot nth input (x) bridge and give it a label
            sp = self.plot_bridge(start_bridge, "x", index=pt_nr)

            # Iterate over next column of bridges (columns)
            # Connect each input bridge which next bridge it should be connected to
            for coord in range(mx_list[0].shape[1]):
                self.plot_connect_points(sp, new_bridges[coord].left_point, line_type=mx_list[0][pt_nr][coord])

            # Create offset, space in Y axis so that next input (x) bridge will be plotted below
            start_bridge += Point(0, self.point_height_offset)
        #

        #
        # Next, iterate over remaining matrices in the list and for each matrix:
        for mx in mx_list[1:-1]:
            # Reinitialize start point - just to make all points in next column start from the same Y height
            start_bridge = Bridge(Point(self.x_s, self.y_s), length=self.bridge_size)
            new_bridges = list(self.set_bridges(mx_list[-1].shape[1], start_bridge))
            # For each point in the current input (or just previous) column
            # connect it to the specific point in next column that it should be connected to
            for pt_nr in range(mx.shape[0]):
                for coord in range(mx.shape[1]):
                    self.plot_connect_points(new_bridges[pt_nr].right_point, new_bridges[coord].left_point, line_type=mx_list[0][pt_nr][coord])
            #
        #

        # Draw next column of bridges that it will connect to
        # Reinitialize start point
        start_bridge = Bridge(Point(self.x_s, self.y_s), length=self.bridge_size)
        last_bridges = list(self.set_bridges(mx_list[-1].shape[1], start_bridge, ["y", LABEL_RIGHT]))

        for pt_nr in range(mx_list[-1].shape[0]):
            for coord in range(mx_list[-1].shape[1]):
                self.plot_connect_points(new_bridges[pt_nr].right_point, last_bridges[coord].left_point, line_type=mx_list[-1][pt_nr][coord])
        #
    #

    def set_bridges(self, mx, start_bridge, params=None):
        y_offset = 0
        for i in range(mx):
            next_bridge = Bridge(start_bridge.right_point + Point(self.x_offset, y_offset), length=self.bridge_size)
            if params == None:
                self.plot_bridge(next_bridge)
            else:
                self.plot_bridge(next_bridge, params[0], i, params[1])
            yield next_bridge
            y_offset += self.point_height_offset
        self.x_offset += self.x_offset
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


    main.plot_scheme([m_in, m_out])

    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()