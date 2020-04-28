import sys
from PyQt4.QtGui import * 
from PyQt4.QtCore import *
INT_MAX = 100000
NEARNESS_THRESHOLD = 10

class BezierWindow(QWidget):
    def __init__(self, t_values=100):
        super(BezierWindow, self).__init__()            
        self.points = []
        self.t_values = t_values
        self.mPixmap = QPixmap()
        self.isModified = True
        self.func = (None, None)
        self.move_index = None

        self.setGeometry(0, 0, 1024, 650)
        self.setWindowTitle('Bezier Drawings - IS F311')    
        self.show()

    def paintEvent(self, event):
        if self.isModified:
            pixmap = QPixmap(self.size())
            pixmap.fill(Qt.white)
            painter = QPainter(pixmap)
            painter.drawPixmap(0, 0, self.mPixmap)
            self.drawBackground(painter)
            self.mPixmap = pixmap
            self.isModified = False
        qp = QPainter(self)
        qp.drawPixmap(0, 0, self.mPixmap)

    def drawBackground(self, qp):
        func, kwargs = self.func
        if func is not None:
            kwargs["qp"] = qp
            func(**kwargs)
        qp.end()

    def addNode(self, qp, point, verbose=True):
        pen = QPen(Qt.blue, 7, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawPoint(point)
        self.points.append(point)
        if len(self.points) > 1:
            pen = QPen(Qt.black, 1, Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(self.points[-2], self.points[-1])
        if verbose:
            print("New point added. Total points: ", len(self.points))

    def redrawNodes(self, qp):
        nodes = self.points
        self.points = []
        for node in nodes:
            self.addNode(qp=qp, point=node, verbose=False)

    def get_nearest_point(self, point):
        currrent_minimum = INT_MAX
        current_index = -1
        for index in range(0, len(self.points)):
            node = self.points[index]
            distance = node - point
            distance = distance.manhattanLength()
            if distance < NEARNESS_THRESHOLD and distance < currrent_minimum:
                currrent_minimum = distance
                current_index = index
        return current_index

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.func = (self.addNode, {"point": QMouseEvent.pos()})
            self.isModified = True
        elif QMouseEvent.button() == Qt.RightButton:
            print("Right Button Clicked: Remove Node") 
            nearest_point = self.get_nearest_point(QMouseEvent.pos())
            if nearest_point == -1:
                print("[Remove Failed] No node found near the place you've clicked.")
                return
            else:
                self.mPixmap.swap(QPixmap());
                self.update()
                del self.points[nearest_point]
                self.func = (self.redrawNodes, {})
                self.isModified = True
        elif QMouseEvent.button() == Qt.MiddleButton:
            print("Middle Button Clicked: Move Node")
            if self.move_index is None:
                nearest_point = self.get_nearest_point(QMouseEvent.pos())
                if nearest_point == -1:
                    print("[Move Failed] No node found near the place you've clicked.")
                    return
                else:
                    self.move_index = nearest_point
                    print("Move: Node selected")
            else:
                self.points[self.move_index] = QMouseEvent.pos()
                self.mPixmap.swap(QPixmap());
                self.update()
                self.func = (self.redrawNodes, {})
                self.isModified = True
                self.move_index = None

        else:
            print("Unidentified click (is this even possible?)")
            return
        self.update()

    def keyPressEvent(self, event):
        user_input = event.key()
        if user_input == Qt.Key_C:
            print("Clear Screen")
            self.mPixmap.swap(QPixmap());
            self.update()
            self.points = []
        elif user_input == Qt.Key_U:
            self.move_index = None
            print("Selection undone. (if made)")
        else:
            print("Unidentified input.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BezierWindow()
    sys.exit(app.exec_())
