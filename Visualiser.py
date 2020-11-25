from random import randint, random
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QPainter, QPicture
from PyQt5.QtWidgets import QApplication
from pyqtgraph import PlotWidget, plot, QtCore
import pyqtgraph as pg
import sys
from numpy import array, zeros, ndenumerate, transpose


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
        self.font = QFont()
        self.font_size = 15
        self.font.setPixelSize(self.font_size)


        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
    #

    # Plot black point and annotation text
    # x, y => coords, name => name of the point, index => index of name,
    # side => is point name on left (0) or right (1)
    def plot_point(self, x, y, name, index, side):
        dot_size= 10
        self.graphWidget.plot([x], [y], symbol='o', symbolSize=dot_size, symbolBrush="k")
        t_up = pg.TextItem(html=name + f"<sub>{index}</sub>", anchor=(1, 1))

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
    def plot_connect_points(self, p_s, p_e, line):
        ln_obj = 0
        if line == 1:
            ln_obj = QtCore.Qt.SolidLine
        elif line == -1:
            ln_obj = QtCore.Qt.DashLine

        line = pg.mkPen(color=(0, 0, 0), width=1.5, style=ln_obj)
        self.graphWidget.plot([p_s[0], p_e[0]], [p_s[1], p_e[1]], pen=line, symbol='o', symbolSize=10, symbolBrush="k")
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
    def plot_bridge(self, point_x, point_y, size):
        line = pg.mkPen(color=(0, 0, 0), width=1.5, style=QtCore.Qt.SolidLine)
        self.graphWidget.plot([point_x, point_x + size], [point_y, point_y], pen=line)
        return (point_x + size, point_y)
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
        m_out_cds = []
        #

        # -----------------------------------
        # phase 1 - plot all points

        # plot input (x)i points
        y_offset = 0
        for i in range(m_in.shape[0]):
            self.plot_point(x_s, y_s + y_offset, "x", i, 0)
            if not self.check_junction(m_in, i, False):
                new_point = self.plot_bridge(x_s, y_s + y_offset, 5)
                m_in_cds += [new_point]
            else:
                m_in_cds += [(x_s, y_s + y_offset)]
            y_offset -= 10

        # plot sum (s)i circles
        y_offset = 0
        for s in range(m_in.shape[1]):
            self.plot_sum(x_s + x_offset, y_s + y_offset, *sum_labels[s], 3)
            m_sum_cds_l += [(x_s + x_offset - 3, y_s + y_offset)]
            m_sum_cds_r += [(x_s + x_offset + 3, y_s + y_offset)]
            y_offset -= 10


        # plot output (y)i points
        y_offset = 0
        for i in range(m_out.shape[1]):
            self.plot_point(x_s + 2 * x_offset, y_s + y_offset, "y", i, 1)
            if not self.check_junction(m_out, i, True):
                new_point = self.plot_bridge(x_s + 2 * x_offset, y_s + y_offset, -5)
                m_out_cds += [new_point]
            else:
                m_out_cds += [(x_s + 2 * x_offset, y_s + y_offset)]
            y_offset -= 10


        # -----------------------------------
        # phase 2 - connect points and sums
        # connect input points and sums
        for cds, val in ndenumerate(m_in):
            self.plot_connect_points(m_in_cds[cds[0]], m_sum_cds_l[cds[1]], val)

        # connect output points and sums
        for cds, val in ndenumerate(m_out):
            self.plot_connect_points(m_sum_cds_r[cds[0]], m_out_cds[cds[1]], val)
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

    m_in, m_out, sum_labels = get_scheme_1()


    main.plot_scheme(m_in, m_out, sum_labels, 20, 60)

    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()