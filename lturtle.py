import turtle
from turtle import RawTurtle
from typing import List
seg_length = 15
alpha_zero = 90
winHeight = 480
winWidth = 600
class Lturtle(RawTurtle):
    """
    Extra class for all the turtle functions in the l-system simulation
    """

    def __init__(self,master, *args, **kwargs):
        """
        Init the lturtle by clearing everythin, going to the bottom of the windo and hiding it also sets
        maximum speed
        :param args:
        :param kwargs:
        """
        super(Lturtle, self).__init__(*args, **kwargs)
        self.master = master
        self.clear()
        self.hideturtle()
        self.penup()
        self.goto(0, -winHeight / 2)
        self.pendown()
        self.speed(0)
        self.isstopped = True



    def reset_turtle(self):
        """
        Resets the turtle, clears everything and going to start position and start direction
        :return:
        """
        self.isstopped = True
        self.clear()
        self.hideturtle()
        self.penup()
        self.goto(0, -winHeight / 2)
        self.pendown()
        self.setheading(alpha_zero)
    def create_empty_stack(self):
        """
        Creates a new empty stack
        :return:
        """
        self.stack = []


    def do_command(self,command:str,angle_value)-> List:
        """
        Evaluates the command given and then does the corresponding action
        :param command: command as char to do
        :param angle_value: value for turning turtle left or right
        :return: the start and end coordinates of the branch if the command was a letter=branch
        """
        self.pd()
        coordinates = [(0, 0),(0,0)]
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

    def draw_sequence(self,string,angle_value,slowly= False,percentage= False):
        """
        Draws a given sequence instantly without storing the coordinates
        :param string: sequence to draw
        :param angle_value: value for turning left and right
        :param slowly: if true draws the sequence slowly
        :param percentage: if true shows percentage of drawn sequenc
        :return: coordinates of drawn sequence
        """
        maxCount = len(string)
        self.create_empty_stack()
        self.reset_turtle()
        self.isstopped = False
        if slowly:
            self.screen.tracer(1,1)
        else:
            self.screen.tracer(0, 0)
        coordinates = []
        for count,command in enumerate(string):
            if self.isstopped:
                break
            coords = self.do_command(command, angle_value)
            if percentage:
                percent = count/ maxCount * 100
                title = "Lindenmayer-System ," + str(round(percent, 1)) + "% gezeichnet..."
                self.master.title(title)
            coordinates.append(coords)
        self.screen.update()
        self.isstopped = False
        return coordinates

    def mark_branch_red(self,start_coordinates,end_coordinates):
        """
        Draws a red line for marking the branch cutted
        :param start_coordinates: start coordinates of branch
        :param end_coordinates: end coordinates of branch
        :return:
        """
        self.penup()
        self.color("red")
        self.goto(start_coordinates)
        self.pendown()
        self.goto(end_coordinates)
        self.penup()
        self.color("black")