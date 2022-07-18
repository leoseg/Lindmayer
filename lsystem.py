from tkinter.messagebox import showerror
import turtle
import tkinter as tk
from tkinter import ttk
import io
from datetime import datetime
from typing import Tuple, List
from lturtle import Lturtle
import setuptools.command.egg_info
from shapely.geometry import LineString
import numpy as np
#--------------------------benötigte Bibliotheken------------------------------
# Installierbar über die Anaconda cmd.exe
# ghostscript wird benötigt, zum speichern der Bilder über den command 
# --> conda install -c conda-forge ghostscript
# pillow wird benötigt, installieren über den command 
# --> conda install -c conda-forge pillow
from PIL import Image
import os
from utils import splitRule, derivation
from utils_cutting import *
import turtle
# Größe des Fensters
winHeight = 480
winWidth = 600
extension = '.png'



class App:
    """
    Main class which creates the app
    """
    # Konstruktor
    def __init__(self, master: tk.Tk):
        """
        Initialization which creates all elements of the gui and initalizes turtles
        :param master: root tk object
        """
        self.master = master

        # Parameter from GUI
        self.isdrawing = False
        self.isstopped = False
        self.cutted= False
        self.rule = tk.StringVar()
        self.axiom = tk.StringVar()
        self.iteration = tk.StringVar()
        self.angle = tk.StringVar()
        self.regrow_axiom = tk.StringVar()
        self.regrow_rule = tk.StringVar()
        self.regrow_iterations = tk.StringVar()

        # Aufbau der Gui
        self.master.resizable(False, False)
        self.master.title("Lindenmayer-System")
        self.drawframe = tk.Canvas(master, width=winWidth, height=winHeight)
        self.drawframe.grid(row=0, column=0, columnspan=5)
        self.growBtn = ttk.Button(master, text="Grow", width=15, state=tk.NORMAL, command=lambda: self.pressgrow())
        self.growBtn.grid(row=1, columnspan=5, pady=5)

        ttk.Label(master, text="Show Step:").grid(row=1, column=3, sticky=tk.W)
        self.itera_cbox = ttk.Combobox(master, state=tk.DISABLED)
        self.itera_cbox.grid(row=2, column=3, columnspan=2, sticky=tk.EW, padx=3)
        self.itera_cbox.bind('<<ComboboxSelected>>', self.changeItemIndex)

        ttk.Label(master, text="Axiom:").grid(row=2, column=0, sticky=tk.W)
        self.axiomEdit = ttk.Entry(master, width=41, textvariable=self.axiom)
        self.axiomEdit.grid(row=2, column=1, sticky=tk.W, padx=3)

        ttk.Label(master, text="Rule:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.ruleEdit = ttk.Entry(master, width=41, textvariable=self.rule)
        self.ruleEdit.grid(row=3, column=1, sticky=tk.W, padx=3)

        ttk.Label(master, text="Iteration:").grid(row=4, column=0, sticky=tk.W)
        self.iterationEdit = ttk.Entry(master, width=41, textvariable=self.iteration)
        self.iterationEdit.grid(row=4, column=1, sticky=tk.W, padx=3)

        ttk.Label(master, text="Angle:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.angleEdit = ttk.Entry(master, width=41, textvariable=self.angle)
        self.angleEdit.grid(row=5, column=1, sticky=tk.W, padx=3)

        self.resetBtn = ttk.Button(master, text="Reset", state=tk.DISABLED, command=lambda: self.pressreset())
        self.resetBtn.grid(row=5, column=3, columnspan=2, sticky=tk.E, padx=3)

        self.cutBtn = ttk.Button(master, text="Cut", state=tk.DISABLED, command=lambda: self.presscut())
        self.cutBtn.grid(row=3, column=3, columnspan=2, sticky=tk.E, padx=3)

        # self.resetcutBtn = ttk.Button(master, text="Reset Cut", state=tk.DISABLED, command=lambda: self.presscutreset())
        # self.resetcutBtn.grid(row=4, column=3, columnspan=2, sticky=tk.E, padx=3)
        # Speicherort der Regeln
        self.rules = {}
        self.regrow_rules = {}

        # Speicherort der Strings
        self.model=[]

        # Speicherort der exportierten Bilder
        self.output = {}

        self.firstcut = True

        # Erstellen der Turtles
        self.screen = turtle.TurtleScreen(self.drawframe)
        #self.screen.delay(0)

        self.turtle = Lturtle(canvas=self.screen)
        self.screen.delay(0)


        self.cut_line_turtle = Lturtle(canvas=self.screen)

        self.redraw_turtle = Lturtle(canvas=self.screen)
        # beinhaltet das aktuelle Bild (wenn geladen) - Initialisieren
        self.loaded_img = None
        self.loaded_bmp = None

        #startwerte
        self.ruleEdit.insert(0,"F=FF-[-F+F+F]+ [+F-F+F]")
        self.angleEdit.insert(0,"22.5")
        self.axiomEdit.insert(0,"F")
        self.iterationEdit.insert(0,2)
    # funktion für GUI-Elemente
    def pressgrow(self):
        """
        Command of the grow button,checks the given rules if they ok draws the lsystem
        :return:
        """
        candraw = False
        # prüfen, ob die Eingabefelder richtig befüllt sind
        axiomOk = self.__checkAxiomFormat(self.axiomEdit.get())
        ruleformatOk = self.__checkRuleFormat(self.ruleEdit.get())
        iterationOk = self.__checkIterationFormat(self.iterationEdit.get())
        angleOk = self.__checkAngleFormat(self.angleEdit.get())
        # Auswertung der Prüfung
        if iterationOk and angleOk and ruleformatOk and axiomOk:
            candraw = True
        if candraw:
            if not self.isdrawing:
                self.isdrawing = True
                self.draw_l_system()
                self.isdrawing = False



    def pressreset(self):
        """
        Command of the reset button clears all turtles and screen
        :return:
        """
        self.isstopped = True
        self.screen.clear()
        self.turtle.reset_turtle()
        self.cut_line_turtle.reset_turtle()
        self.redraw_turtle.reset_turtle()
        self.coordinates = []
        self.itera_cbox['values'] = [' ']
        self.itera_cbox.current(0)
        self.itera_cbox['state'] = 'disabled'
        self.resetBtn['state'] = 'disabled'
        self.cutBtn['state'] = 'disabled'


    def click_fun(self, x, y):
        """
        Function that gets called when mouse is clicked, evaluates two clicks for drawing a cutting line
        :param x: x coordinate of mouse
        :param y: y coordiante of mouse
        :return:
        """
        self.click_num = self.click_num + 1
        # gets first coordinate of mouse click
        if self.click_num == 1:
            self.cut_line_turtle.penup()
            self.cut_line_turtle.goto(x, y)
            self.cut_line.append((x,y))

        #gets second coordinates, evaluate if a branch was hitted if yes cuttes the string and opens a window for
        # inserting rules if no branch was hitted resets the click counter and shows an error
        if self.click_num == 2:
            self.cut_line_turtle.pendown()
            self.cut_line_turtle.goto(x, y)
            self.cut_line.append((x,y))
            self.cutting_index = calc_branch_index_cuted_by_line(self.coordinates,self.cut_line)

            if self.cutting_index != 0:
                self.cut_line_turtle.mark_branch_red(self.coordinates[self.cutting_index][0],self.coordinates[self.cutting_index][1])
                self.__create_cutted_string()
                self.turtle.reset_turtle()
                self.redraw_turtle.draw_sequence(self.cutted_string, self.angle_value)
                self.cut_window()
            else:
                showerror("Error","No branch hitted with cutting line, Try again")
                self.click_num = 0
                self.cut_line_turtle.clear()

    def pressconfirm(self):
        """
        Function if the confirm button in the cut window was pressed checks rules and if okay starts drawing the
        new tree
        :return:
        """
        ruleformatOk = self.__checkRuleFormat(self.regrow_rule.get())
        axiomformatOk = self.__checkAxiomFormat(self.regrow_axiom.get())
        iterationformatOk = self.__checkIterationFormat(self.regrow_iterations.get())
        if ruleformatOk and axiomformatOk and iterationformatOk:
            self.popup.destroy()
            self.click = 0

            self.isstopped = True
            #self.screen.clear()
            if not self.isdrawing:
                self.isdrawing = True
                self.draw_after_cut()
                self.isdrawing = False


    def presscancel(self):
        """
        Gets called if cancel button of cut window is clicked, destroys window and draws old uncutted tree
        :return:
        """
        self.popup.destroy()
        self.click = 0
        self.cut_line_turtle.clear()
        self.redraw_turtle.reset_turtle()
        self.turtle.draw_sequence(self.model[self.choosen_iteration],self.angle_value)

    def cut_window(self):
        """
        Functions that creates the cut window
        :return:
        """
        # Speicherort der Regeln
        self.popup = tk.Toplevel(self.master)
        self.regrow_entry = ttk.Entry(self.popup, width=41, textvariable=self.regrow_rule)
        self.regrow_axiom_entry = ttk.Entry(self.popup,width=41,textvariable=self.regrow_axiom)
        self.regrow_iterations_entry = ttk.Entry(self.popup,width=41,textvariable=self.regrow_iterations)
        self.regrow_confirm = ttk.Button(self.popup, text="Bestätigen", width=15, state=tk.NORMAL,
                                         command=lambda: self.pressconfirm())
        self.cancel = ttk.Button(self.popup,text="Abbrechen",width=15, state=tk.NORMAL,
                                         command=lambda: self.presscancel())

        self.iterationlabel = ttk.Label(self.popup, text="Iterations:")
        self.axiomlabel = ttk.Label(self.popup, text="Axiom:")
        self.ruleslabel = ttk.Label(self.popup, text="Regel:")


        self.axiomlabel.pack()
        self.regrow_axiom_entry.pack()
        self.ruleslabel.pack()
        self.regrow_entry.pack()
        self.iterationlabel.pack()
        self.regrow_iterations_entry.pack()
        self.regrow_confirm.pack()
        self.cancel.pack()


        # setze startdaten
        if self.firstcut:
            self.regrow_axiom_entry.insert(0,"F")
            self.regrow_entry.insert(0,"F=FF-[-F+F]+[-F+F]")
            self.regrow_iterations_entry.insert(0,1)
            self.firstcut = False


    def presscut(self):
        """
        If cut button is clicked sets function for click on screen
        :return:
        """
        self.isstopped = True
        self.cut_line = [] #np.empty([2, 2])
        self.click_num = 0

        self.screen.onclick(self.click_fun)


    def __create_cutted_string(self):
        """
        Cuts the plant at the nearest branch to the intersection point of the cutting line by removing the
        corresponding chars in the string and coordinates
        :param coordinates_cutting_line: start and end coordinates of the cutting line
        :return:
        """

        self.tribe_cutted = check_if_tribe_cutted(self.complete_l_string,self.cutting_index)
        if self.tribe_cutted:
            self.coordinates = self.coordinates[:self.cutting_index]
            self.cutted_branch_direction = ""
            self.cutted_string = self.complete_l_string[:self.cutting_index]
        else:
            self.end_index = get_end_index(self.cutting_index,self.complete_l_string)
            self.coordinates = self.coordinates[:self.cutting_index] + self.coordinates[self.end_index :]
            self.cutted_string = self.complete_l_string[:self.cutting_index] + self.complete_l_string[self.end_index :]


    def changeItemIndex(self, event):
        """
        Loads the image file for the given iteration selected
        :param event:
        :return:
        """
        # initialisieren
        self.turtle.reset_turtle()
        self.redraw_turtle.reset_turtle()
        self.cut_line_turtle.reset_turtle()
        self.loaded_bmp = None
        self.loaded_img = None
        m = re.search(r"\d", self.itera_cbox.get())
        self.choosen_iteration = int(self.itera_cbox.get()[m.start()])

        sequence = self.model[self.choosen_iteration]
        self.coordinates = self.turtle.draw_sequence(sequence,self.angle_value)
        self.complete_l_string = sequence
    def __checkAxiomFormat(self, axiomStr):
        """
        Checks if the axiom string has the correct format
        :param axiomStr: str with axiom
        :return: true if correct
        """
        if len(axiomStr) == 0:
            showerror('Missing Entry', 'The "Axiom" must not be empty.')
            return False
        elif not axiomStr in ["F", "G", "R", "L"]:
            showerror('Wrong Entry', 'The axiom must be an element from ("F", "G", "R", "L").')
            return False
        else:
            return True

    def __checkAngleFormat(self, angleStr):
        """
        Checks if the angle string has the correct format
        :param angleStr: str with angle
        :return: true if correct
        """
        try:
            if not angleStr.count('.') == 1:
                showerror('Wrong Format', 'In "Angle" must be a number with "." (dot). Do not use "," (comma).')
                return False
            elif float(angleStr) < 0.0:
                showerror('Wrong Format', '"Angle" must bigger then 0.')
                return False
            else:
                return True
        except BaseException:
            showerror('Wrong Format', 'In "Angle" must be a number with "." (dot). Do not use "," (comma).')
            return False

    def __checkIterationFormat(self, iterationStr):
        """
        Checks if the iteration string has the correct format
        :param iterationStr: str with iteration number
        :return: true if correct
        """
        if not iterationStr.isnumeric():
            showerror('Wrong Format', '"Iteration" must be a positive number.')
            return False
        else:
            return True

    def __checkRuleFormat(self, ruleStr):
        """
        Checks if the rule string has the correct format
        :param ruleStr: str with rule
        :return: true if correct
        """
        if ruleStr.count('=') > 1:
            showerror('Wrong Format', '"Rule" must contain only one "=", e.g. "F=FF+[+F-F-F]-[-F+F+F]".')
            return False
        elif len(ruleStr) == 0:
            showerror('Missing Entry', 'The "Rule" must not be empty.')
            return False
        elif not '=' in ruleStr:
            showerror('Wrong Format', '"Rule" must contain "=", e.g. "F=FF+[+F-F-F]-[-F+F+F]".')
            return False
        else:
            return True

    def __countModels(self, model):
        """
        For each model gets the length and saves it to an list
        :param model: list with all models
        :return: list with lengths of models
        """
        posArr = []
        modelCount = len(model)
        for step in range(1, modelCount):
            posArr.append(len(model[step]) - 1)
        return posArr


    def __fill_combobox(self, maxiteration):
        """
        Fills the selectbox with iterations
        :param maxiteration: number of iterations
        :return:
        """
        self.output.clear()
        self.itera_cbox['state'] = 'readonly'
        self.itera_cbox['values'] = []
        cbItems = []
        for i in range(0, maxiteration):
            cbItems.append('Iteration ' + str(i + 1))
        self.itera_cbox['values'] = cbItems


    def draw_l_system(self):
        """
        Draws the l-system
        :return:
        """

        # gets user values (angel, rule,axiom)
        self.isstopped = False
        self.rules = splitRule(self.rule.get())
        axiom = self.axiom.get()
        iterations = int(self.iteration.get())
        self.angle_value = float(self.angle.get())

        # derivates models
        self.model = [axiom]
        self.model = derivation(self.model, iterations, self.rules)
        self.complete_l_string = self.model[-1]

        #initialize turtle
        self.turtle.create_empty_stack()
        self.turtle.reset_turtle()

        #draw system and saves coodirnates
        self.coordinates =self.__evaluate_sequence_to_draw(self.model[-1])
        self.__fill_combobox(iterations)
        self.old_iterations =iterations

        # enables buttons
        self.resetBtn['state'] = 'normal'
        self.cutBtn['state'] = 'normal'

        self.choosen_iteration=len(self.model) -1
    # public funktionen - End
    def draw_after_cut(self):
        """
        Draws the l-system after the cut
        :return:
        """

        # initialize turtle
        self.turtle.create_empty_stack()
        self.turtle.reset_turtle()
        self.itera_cbox["state"] = "disabled"
        self.isstopped = False

        # derivates regrow models
        self.regrow_rules = splitRule(self.regrow_rule.get().lower())
        iterations = int(self.regrow_iterations.get())
        regrow_model = derivation([self.regrow_axiom.get().lower()], iterations, self.regrow_rules)

        # derivates models
        self.model = derivation(self.model, iterations, self.rules)
        self.__insert_regrow_model_into_model(regrow_model)
        #draws new system with cutted branch
        self.__evaluate_sequence_to_draw(self.model[-1], iterations + self.old_iterations)
        self.__fill_combobox(iterations + self.old_iterations)

        # enables buttons
        self.resetBtn['state'] = 'normal'
        self.cutBtn['state'] = 'disabled'

    def __insert_regrow_model_into_model(self,regrow_model):
        """
        Inserts the new regrow model into the models
        :param regrow_model: list of regrow models
        :return:
        """
        for counter,regrow in enumerate(regrow_model):
            old_model = self.model[self.old_iterations+counter]
            if self.tribe_cutted:
                old_model = old_model[:self.cutting_index]+regrow
            else:
                old_model = old_model[:self.cutting_index] +regrow+ old_model[self.end_index:]
            self.model[self.old_iterations + counter] = old_model


    def __evaluate_sequence_to_draw(self,sequence:str):
        """
        Evalutes the sequence which should be drawn and changes title to percentage
        :param sequence: sequence which should be drawn
        :param iterations: number of iterations
        :return:
        """
        self.screen.tracer(1,1)
        # For counting percentage of drawing
        maxCount = len(sequence)
        coordinates = []
        for count,command in enumerate(sequence):
            if self.isstopped:
                break
            coordinates_turtle= self.turtle.do_command(command, self.angle_value)
            coordinates.append(coordinates_turtle)
            percent = count/ maxCount * 100
            title = "Lindenmayer-System ," + str(round(percent, 1)) + "% gezeichnet..."
            self.master.title(title)
        self.master.title("Lindenmayer-System")
        self.isstopped = False
        return coordinates

if __name__ == "__main__":
    # Standart-Fenster erzeugen
    root = tk.Tk()
    # App und Fenster mit passenden Eigenschaft befüllen
    app = App(root)
    # App Loop um auf Button drücke zu reagieren
    root.mainloop()
