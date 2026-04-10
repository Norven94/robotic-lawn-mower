#How the obstacles work
#Shape
class rectangleobstacles:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.width = size
        self.height = size
    def is_hitting( self, robot_x, robot_y, padding):
        within_x =self.x - padding<= robot_x <= self.x + self.width + padding
        within_y = self.y - padding<= robot_y <= self.y + self.height + padding
        return within_x and within_y

