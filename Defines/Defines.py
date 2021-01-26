from collections import namedtuple
from random import randint, random
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QToolBar, QStatusBar, QGridLayout, QWidget, QGroupBox, QVBoxLayout, QFrame, QPushButton, \
    QLabel, QHBoxLayout, QProgressBar, QRadioButton, QButtonGroup, QTextEdit, QCheckBox, QFileDialog, QFrame,\
    QSizePolicy, QComboBox
from qdarkstyle import load_stylesheet
import sys
from numpy import array, zeros, ndenumerate, transpose, savetxt, int as int_np
from Defines.Items import *
from Examples.examples import *
import PyQt5.QtCore as pqtc
from PyQt5.QtWidgets import QTextBrowser, QSpinBox, QTextEdit, QLineEdit, QDialog
from glob import glob
from os import path

LABEL_LEFT  = 0
LABEL_RIGHT = 1

BRIDGE_LEFT  = 0
BRIDGE_RIGHT = 1

# Define order in which the IN matrices will be passed
# Example: Y = A * B * SUM * D (equation), list of matrices: [A, B, S, D], ORDER: ORDER_LR
ORDER_LR = 1
ORDER_RL = 0

options_print = ["Default Window", "External - A4"]

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    # Get point from another point
    @classmethod
    def fromPoint(cls, point):
        # assert type(point) == type(Point)
        return cls(point.x, point.y)

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        if isinstance(other, int):
            return Point(self.x + other, self.y + other)
    #

    def __str__(self):
        return str("(x: " + str(self.x) + " y: " + str(self.y) + ")")
#

class Bridge:
    def __init__(self, left_point, length=0, bridge_size=BRIDGE_RIGHT):
        self.left_point  = left_point
        self.right_point = left_point + Point(x=length)
        self.length      = length

    def __str__(self):
        return str("Left point: " + str(self.left_point) + " Right point: " + str(self.right_point))

    # Add Point() (offset) to a bridge's points
    def __add__(self, other):
        if isinstance(other, Point):
            return Bridge(self.left_point + other, self.length)