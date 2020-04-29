"""
	Draw bezier curve for a given set of points using the recursive de Castlejau algorithm. Implemented
	using PyQt4
"""
import sys
from PyQt4.QtGui import * 
from PyQt4.QtCore import *
INT_MAX = 100000
NEARNESS_THRESHOLD = 10
NUM_T_VALUES = 2000  

class BezierWindow(QWidget):
    def __init__(self, t_values=100):
        super(BezierWindow, self).__init__()            
        self.points = []
        self.t_values = t_values
        self.mPixmap = QPixmap()
        self.isModified = True
        self.func = (None, None)
        self.move_index = None
        self.bezier_drawn = False
        self.setGeometry(0, 0, 1024, 650)
        self.setWindowTitle('Bezier Drawings - IS F311')    
        self.show()

    def get_bezier_point(self, points, t):
	    '''
			For a certain value of t, get the point on the final bezier curve. Returns a QPoint object of the 
			point on the bezier curve 
	    '''
        values = []
        for i in range(1, len(points)):
            values.append((points[i] * t) + (points[i-1] * (1-t)))
        if len(values) == 1:
            return values[0]
        else:
            return self.get_bezier_point(values, t)

    def drawBezier(self, qp):
    	'''
			Draw bezier curve on the QPainter object qp
	    '''
        if not self.bezier_drawn:
            t_values = [(i *1.0)/NUM_T_VALUES for i in range(0, NUM_T_VALUES)]
            pen = QPen(Qt.blue, 3, Qt.SolidLine)
            qp.setPen(pen)
            for t in t_values:
                bezier_point = self.get_bezier_point(self.points, t)
                qp.drawPoint(bezier_point)
            self.bezier_drawn = True

    def paintEvent(self, event):
    	'''
			Function triggered on every update() call.
	    '''
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
        '''
			Add a new control point. 
	    '''
        pen = QPen(Qt.red, 7, Qt.SolidLine)
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
    	'''
			Plot all the control points and lines again. 
	    '''
        nodes = self.points
        self.points = []
        for node in nodes:
            self.addNode(qp=qp, point=node, verbose=False)

    def get_nearest_point(self, point):
    	'''
			Get the index of the nearest point to the argument point, from 
			the list of points in self.points.  
	    '''
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
    	'''
    		processing mouse events
    	'''
        if QMouseEvent.button() == Qt.LeftButton:
            self.points.append(QMouseEvent.pos())
            self.mPixmap.swap(QPixmap());
            self.update()
            self.func = (self.redrawNodes, {})
            self.isModified = True
            self.bezier_drawn = False
        elif QMouseEvent.button() == Qt.RightButton:
            print("Right Button Clicked: Remove Node") 
            nearest_point = self.get_nearest_point(QMouseEvent.pos())
            if nearest_point == -1:
                print("[Remove Failed] No node found near the place you've clicked.")
                return
            else:
                self.move_index = None
                self.mPixmap.swap(QPixmap());
                self.update()
                del self.points[nearest_point]
                self.func = (self.redrawNodes, {})
                self.isModified = True
                self.bezier_drawn = False
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
                self.bezier_drawn = False
        else:
            print("Unidentified click (is this even possible?)")
            return
        self.update()

    def keyPressEvent(self, event):
    	'''
    		processing keyboard events
    	'''
        user_input = event.key()
        if user_input == Qt.Key_C:
            print("Clear Screen (C)")
            self.mPixmap.swap(QPixmap());
            self.update()
            self.points = []
            self.bezier_drawn = False
        elif user_input == Qt.Key_U:
            print("Selection undone (U)")
            self.move_index = None
        elif user_input == Qt.Key_D:
            print("Draw Bezier Curve (D)")
            self.func = (self.drawBezier, {})
            self.isModified = True
            self.update()
        if user_input == Qt.Key_R:
            print("Refresh Screen (R)")
            self.mPixmap.swap(QPixmap());
            self.update()
            self.func = (self.redrawNodes, {})
            self.isModified = True
            self.update()
            self.bezier_drawn = False
        else:
            print("Unidentified keyboard input.")

if __name__ == '__main__':
	'''
		Driver code
	'''
    app = QApplication(sys.argv)
    ex = BezierWindow()
    sys.exit(app.exec_())
