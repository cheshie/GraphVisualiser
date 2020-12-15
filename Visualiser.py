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
from examples import *


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
        # TODO: how to draw ellipse as ideal circle????
        # TODO: floats here cause warning. Understand why
        p.drawEllipse(int(self.center[0]), int(self.center[1] - self.radius), self.radius * 2, self.radius * 2)
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
        self.x_s = 100
        self.y_s = 100

        self.sum_radius = 5
        self.point_offset = Point(x=2, y=-2)
        self.scale_factor = -self.point_height_offset / 4
        self.sum_label = 's'
        self.input_label = 'x'
        self.out_label = 'y'

        self.font.setPixelSize(self.font_size)

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
    #

    # in case there is junction, bridge must be plotted to extend point's arm
    # x, y is just point coords
    # size is the length of arm
    # dir 1 => left, 0 => right (direction of point's arm/bridge)
    # returns => coords of the end of bridge, will be the new point
    def plot_bridge(self, bridge, label="", index=0, label_side=LABEL_LEFT):
        if label != "":
            label_item = None
            if label_side == LABEL_LEFT:
                label_item = pg.TextItem(html=label + f"<sub>{index}</sub>", anchor=(1, 1))
                label_item.setPos(bridge.left_point.x - self.label_offset, bridge.left_point.y - self.label_height)
            elif label_side == LABEL_RIGHT:
                label_item = pg.TextItem(html=label + f"<sub>{index}</sub>", anchor=(0, 1))
                label_item.setPos(bridge.right_point.x + self.label_offset, bridge.right_point.y - self.label_height)
            if label_item is not None:
                label_item.setFont(self.font)
                self.graphWidget.addItem(label_item)

        #TODO: should I add offset to these points like with labels [1,1] ??
        self.graphWidget.plot([bridge.left_point.x], [bridge.left_point.y], symbol='o', symbolSize=self.dot_size, symbolBrush="k")
        self.graphWidget.plot([bridge.left_point.x, bridge.right_point.x], [bridge.left_point.y, bridge.right_point.y], pen=self.bridge_line)
        self.graphWidget.plot([bridge.right_point.x], [bridge.right_point.y], symbol='o', symbolSize=self.dot_size, symbolBrush="k")
        return bridge
    #

    # Plot circle with symbol inside, representing specific sum
    # on both sides of circle plot bridges and return right point of right bridge
    # next_bridge => right point of previous bridge that sum will be plotted on
    # index => index of symbol plotted inside sum
    # symbol => sum symbol inside sum
    def plot_sum(self, left_bridge, index=0):
        # get starting point of circle sum and plot starting bridge
        # right_point = self.plot_bridge(left_bridge)
        # create circle, which starts in the middle of right side (coordinates of right point of left bridge)
        c_sum = CircleItem([left_bridge.right_point.x, left_bridge.right_point.y], self.sum_radius)
        # plot right bridge
        right_bridge = Bridge(Point(left_bridge.right_point.x + self.sum_radius + self.bridge_size, left_bridge.right_point.y), self.bridge_size)
        self.plot_bridge(right_bridge)

        # Add text label to sum
        l_sum = pg.TextItem(html=str(self.sum_label) + f"<sub>{index}</sub>", anchor=(1, 1))
        l_sum.setPos(left_bridge.right_point.x + self.sum_radius + self.point_offset.x, left_bridge.right_point.y + self.point_offset.y)
        l_sum.setFont(self.font)
        #

        # plot sum circle and label
        self.graphWidget.addItem(c_sum)
        self.graphWidget.addItem(l_sum)

        # return right bridge
        return right_bridge
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
    # b_s is a (start) Bridge with start coordinates (x, y)
    # b_e is a (end) Bridge with end coordinates (x, y)
    def link_bridge(self, b_s, b_e, line_type=1):
        ln_obj = 0
        if line_type == 1:
            ln_obj = QtCore.Qt.SolidLine
        elif line_type == -1:
            ln_obj = QtCore.Qt.DashLine

        if line_type != 0:
            line = pg.mkPen(color=(0, 0, 0), width=1.5, style=ln_obj)
            self.graphWidget.plot([b_s.right_point.x, b_e.left_point.x],
                              [b_s.right_point.y, b_e.left_point.y],
                              pen=line, symbol='o', symbolSize=10, symbolBrush="k")
    #

    # Given set of input points m_in, output points m_out and x_s, y_s as starting coords
    def plot_scheme(self, mx_list, sum_matrix_index=0):
        # Length of list of matrices in equation should be at least 3. Two combinations and one sum
        assert len(mx_list) >= 3
        # Matrix index must be given (and it will never be 1st matrix, that's why 0 here)
        assert sum_matrix_index != 0

        # Create starting bridge => x0
        start_bridge = Bridge(Point(self.x_s, self.y_s), length=self.bridge_size)
        # Move to the next offset in order to draw entire second column of bridges
        start_bridge += Point(self.x_offset)

        # Adjusting height of bridge - centering
        # set offset for Y so that graph will be nicely stretched and centered
        # Do it only if matrix dimensions are not equal
        if mx_list[0].shape[0] != mx_list[0].shape[1]:
            start_bridge += Point(y=mx_list[0].shape[1] * self.scale_factor)
        # Draw second column, that input (x) column will connect to
        # Save all coordinates of bridges in a new_bridges list
        new_bridges   = list(self.set_bridges(mx_list[0].shape[1], start_bridge))

        # Secondly, iterate over input (x) points and connect each of them with specific
        # bridge they should be connected to
        # Iterate over rows (inputs)
        # Reinitialize start_bridge. This is because now the rest of bridges will be plotted and connected, one by one
        start_bridge = Bridge(Point(self.x_s, self.y_s), length=self.bridge_size)
        for pt_nr in range(mx_list[0].shape[0]):
            # Plot nth input (x) bridge and give it a label
            sb = self.plot_bridge(start_bridge, self.input_label, index=pt_nr)

            # Iterate over next column of bridges (columns)
            # Connect each input bridge which next bridge it should be connected to
            for coord in range(mx_list[0].shape[1]):
                self.link_bridge(sb, new_bridges[coord], mx_list[0][pt_nr][coord])

            # Create offset, space in Y axis so that next input (x) bridge will be plotted below
            start_bridge += Point(y=self.point_height_offset)
        #

        # set offset for next bridge - in X axis, so that new bridge will be further
        # also, set offset for Y so that graph will be nicely stretched and centered
        start_bridge = Bridge(Point(self.x_s, self.y_s), length=self.bridge_size) + Point(x=self.x_offset)
        # Next, iterate over remaining matrices in the list and for each matrix:
        # Reinitialize start point and add x offset to it. This way next bridge
        # is prepared to be plotted in next column
        # set offset for Y so that graph will be nicely stretched and centered
        # Do it only if matrix dimensions are not equal
        for i, mx in enumerate(mx_list[1:-1]):
            # Adjusting height of bridge - centering
            # Adjust height of next columns of bridges so that entire graph will
            # be nicely centered
            # (and do it only for equations that have more than 3 matrices)
            if len(mx_list) > 3:
                if i + 1 < sum_matrix_index:
                    start_bridge += Point(y=mx_list[0].shape[1] * self.scale_factor)
                if i + 1 > sum_matrix_index:
                    start_bridge += Point(y=mx_list[0].shape[1] * -self.scale_factor)
            elif len(mx_list) == 3:
                start_bridge += Point(y=mx_list[0].shape[1] * self.scale_factor)

            # Executed when sum matrix met
            if i + 1 == sum_matrix_index:
                # draw column of sums
                new_bridges = list(self.set_sums(len(mx), start_bridge))
                # right bridge of sum will be next bridge
                start_bridge = new_bridges[0]
                # Adjusting height of bridge - centering
                # add offset to bridge in order to prepare it for next column
                start_bridge += Point(y=mx_list[0].shape[1] * -self.scale_factor * 2)
            # Executed when normal matrix with combinations met
            else:
                # Reinitialize start point - just to make all points in next column start from the same Y height
                new_bridges = list(self.set_bridges(mx.shape[0], start_bridge + Point(x=self.x_offset)))
                # For each point in the current input (or just previous) column
                # connect it to the specific point in next column that it should be connected to
                if sum_matrix_index in (i, i-1) and len(mx_list) > 3:
                    start_bridge += Point(y=mx_list[0].shape[1] * self.scale_factor * 2)

                for index, el in ndenumerate(transpose(mx)):
                    if index[1] == 0:
                        start_bridge.right_point.y += self.point_height_offset
                    self.link_bridge(start_bridge, new_bridges[index[1]], mx[index[1]][index[0]])
                start_bridge = new_bridges[0]

            # Adjusting height of bridge - centering
            if i + 1 == sum_matrix_index:
                if len(mx_list) > 3:
                    start_bridge += Point(y=mx_list[0].shape[1] * self.scale_factor * 2)
                if len(mx_list) == 3:
                    start_bridge += Point(y=mx_list[0].shape[1] * self.scale_factor)
            #
        #

        # Adjusting height of bridge - centering
        # set offset for next bridge - in X axis, so that new bridge will be further
        # also, set offset for Y so that graph will be nicely stretched and centered
        start_bridge += Point(self.x_offset)
        if mx_list[-1].shape[0] != mx_list[0].shape[1]:
            start_bridge += mx_list[0].shape[1] * -self.scale_factor
        # Draw last column of bridges that it will connect to
        last_bridges = list(self.set_bridges(mx_list[-1].shape[1], start_bridge, [self.out_label, LABEL_RIGHT]))
        for pt_nr in range(mx_list[-1].shape[0]):
            for coord in range(mx_list[-1].shape[1]):
                self.link_bridge(new_bridges[pt_nr], last_bridges[coord], mx_list[-1][pt_nr][coord])
    #

    # For given starting bridge, draw column of bridges, number indicated by mx_len
    def set_bridges(self, mx_len, start_bridge, params=None):
        for i in range(mx_len):
            # Plot bridge without label
            if params is None:
                self.plot_bridge(start_bridge)
            # Plot bridge with label
            else:
                self.plot_bridge(start_bridge, params[0], i, params[1])
            # yield coordinates of each bridge
            yield start_bridge
            # move downwards to draw next bridge
            start_bridge += Point(y=self.point_height_offset)
    #

    # For given starting bridge, draw column of sums, number indicated by mx_len
    def set_sums(self, mx_len, start_bridge):
        for i in range(mx_len):
            # plot sum (circle and right-side bridge) next to sum's left side bridge
            # meaning: it does not plot left bridge, only plots circle and right bridge to it
            next_bridge = self.plot_sum(start_bridge, i)
            # Add coordinates of right bridge
            yield next_bridge
            # Take vertical offset into consideration
            start_bridge += Point(y=self.point_height_offset)
    #
#


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()

    main.plot_scheme(example_2[::-1], sum_matrix_index=example_2_sum_i)

    main.show()
    sys.exit(app.exec_())