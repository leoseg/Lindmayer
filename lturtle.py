from turtle import RawTurtle
from typing import List

class Lturtle(RawTurtle):

    def __init__(self, winHeight,*args, **kwargs):
        super(Lturtle, self).__init__(*args, **kwargs)
        self.clear()
        self.hideturtle()
        self.penup()
        self.goto(0, -winHeight / 2)
        self.pendown()


    def reset_turtle(self,winHeight):
        self.clear()
        self.hideturtle()
        self.penup()
        self.goto(0, -winHeight / 2)
        self.pendown()
    def create_empty_stack(self):
        self.stack = []


    def do_command(self,command:str,seg_length,angle_value)-> List:
        self.pd()
        coordinates = [(0, 0), (0, 0)]
        if command in ["F", "G", "R", "L", "f", "g", "r", "l"]:
            if command in ["F", "G", "R", "L"]:
                self.pencolor("black")
            if command in ["f", "g", "r", "l"]:
                self.pencolor("blue")
            start_coordinate = self.pos()
            self.forward(seg_length)
            end_coordinate = self.pos()
            coordinates = [start_coordinate, end_coordinate]
        elif command == "+":
            self.left(angle_value)
        elif command == "-":
            self.right(angle_value)
        elif command == "[":
            self.stack.append((self.position(), self.heading()))
        elif command == "]":
            self.pu()  # pen up - not drawing
            position, heading = self.stack.pop()
            self.goto(position)
            self.setheading(heading)
        return coordinates