from tkinter.messagebox import showerror
import turtle
import tkinter as tk
from tkinter import ttk
import io
from datetime import datetime
from typing import Tuple, List

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
# Größe des Fensters
winHeight = 480
winWidth = 600
extension = '.png'


class App:
    # Konstruktor
    def __init__(self, master: tk.Tk):
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

        self.resetcutBtn = ttk.Button(master, text="Reset Cut", state=tk.DISABLED, command=lambda: self.presscutreset())
        self.resetcutBtn.grid(row=4, column=3, columnspan=2, sticky=tk.E, padx=3)
        # Speicherort der Regeln
        self.rules = {}
        self.regrow_rules = {}

        # Speicherort der Strings
        self.model=[]

        # Speicherort der exportierten Bilder
        self.output = {}
        # Speicherort für die namen der schnitt indizes
        self.model_cut_images=[]
        self.model_indices_of_cuts=[]
        # Erstellen der Turtle
        self.screen = turtle.TurtleScreen(self.drawframe)
        self.turtle = turtle.RawTurtle(self.screen)
        self.__initTurlteStartPos()

        self.cut_line_turtle = turtle.RawTurtle(self.screen)
        self.cut_line_turtle.hideturtle()
        # beinhaltet das aktuelle Bild (wenn geladen) - Initialisieren
        self.loaded_img = None
        self.loaded_bmp = None

        #startwerte
        self.ruleEdit.insert(0,"F=FF-[-F+F+F]+ [+F-F-F]")
        self.angleEdit.insert(0,"22.5")
        self.axiomEdit.insert(0,"F")
        self.iterationEdit.insert(0,2)
    # funktion für GUI-Elemente
    def pressgrow(self):
        """Command des Grow-Buttons"""
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
        """Command des Reset-Buttons"""
        self.isstopped = True
        self.screen.clear()
        self.__initTurlteStartPos()
        self.itera_cbox['values'] = [' ']
        self.itera_cbox.current(0)
        self.itera_cbox['state'] = 'disabled'
        self.resetBtn['state'] = 'disabled'
        self.cutBtn['state'] = 'disabled'
        self.resetcutBtn['state'] = 'disabled'
        self.cutted = False
        for f in os.listdir("/images"):
            try:
                os.remove(f)
            except OSError as e:
                print("Error: %s : %s" % (f, e.strerror))

    def click(self, x, y):
        self.click_num = self.click_num + 1
        if self.click_num == 1:
            self.cut_line_turtle.penup()
            self.cut_line_turtle.goto(x, y)
            self.cut_line.append((x,y))

        if self.click_num == 2:
            self.cut_line_turtle.pendown()
            self.cut_line_turtle.goto(x, y)
            self.cut_line.append((x,y))
            self.calc_branch_index_cuted_by_line()
            if self.cutting_index != 0:
                self.cut_window()
            else:
                showerror("Error","No branch hitted with cutting line, Try again")
                self.click_num = 0
                self.cut_line_turtle.clear()

    def pressconfirm(self):
        ruleformatOk = self.__checkRuleFormat(self.regrow_rule.get())
        axiomformatOk = self.__checkAxiomFormat(self.regrow_axiom.get())
        iterationformatOk = self.__checkIterationFormat(self.regrow_iterations.get())
        if ruleformatOk and axiomformatOk and iterationformatOk:
            self.popup.destroy()
            self.click = 0
            self.cut_plant(self.cut_line)
            self.isstopped = True
            self.screen.clear()
            self.__initTurlteStartPos()

            if not self.isdrawing:
                self.isdrawing = True
                self.draw_l_system()
                self.isdrawing = False


    def presscancel(self):
        self.popup.destroy()
        self.click = 0
        self.cut_line_turtle.clear()
    def cut_window(self):
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
        self.regrow_axiom_entry.insert(0,"F")
        self.regrow_entry.insert(0,"F=FF-[-F+F]")
        self.regrow_iterations_entry.insert(0,2)


    def presscut(self):
        """Command des Cut-Buttons"""
        self.isstopped = True
        self.cut_line = [] #np.empty([2, 2])
        self.click_num = 0

        self.screen.onclick(self.click)

    def presscutreset(self):
        """Command des ResetCut-Buttons"""
        self.__initTurlteStartPos()
        self.loaded_bmp = None
        self.loaded_img = None
        filename = self.model_cut_images[-1]
        # prüfen ob ein Bild geladen wurde
        try:
            self.loaded_img = tk.PhotoImage(file=filename)
            self.model_cut_images.pop()
        except BaseException:
            showerror('File not found', 'File "' + filename + '" does not exist.')
            return
        self.drawframe.create_image((0, 0), image=self.loaded_img)
        self.drawframe.grid(row=0, column=0, columnspan=5)
        self.model = self.model[:self.model_indices_of_cuts[-1]]
        self.model_indices_of_cuts.pop()
        if len(self.model_indices_of_cuts) == 1:
            self.resetcutBtn['state'] = 'disabled'

    def calc_branch_index_cuted_by_line(self):
        self.cutting_index = 0
        for count, coordinates in enumerate(self.coordinates):
            if self.__check_segments_are_crossing(self.cut_line, coordinates):
                self.cutting_index = count
                break

    def cut_plant(self, coordinates_cutting_line: List[Tuple[float, float]]):
        """
        Cuts the plant at the nearest branch to the intersection point of the cutting line by removing the
        corresponding chars in the string
        :param coordinates_cutting_line: start and end coordinates of the cutting line
        :return:
        """

        start_index,end_index = self.__gets_start_end_to_cut(self.cutting_index)
        self.cutted_branch_index= start_index
        self.cutted_string = self.complete_l_string[:start_index+1] + self.regrow_axiom.get().lower()+self.complete_l_string[end_index:]
        self.cutted= True

    def __gets_start_end_to_cut(self, cutting_index: int) -> Tuple[int, int]:
        """
        Loops trough string to find the indices of the corresponding end and start brackets between which the
        string should be cutted
        :param cutting_index: the index of the branch in the string which the cutting line intersected
        :return: start and end index of '[' and ']' bracket
        """
        next = "!"
        start_index = cutting_index
        while (next != "["):
            start_index = start_index -1
            next = self.complete_l_string[start_index]

        end_index = cutting_index
        while (next != "]"):
            end_index += 1
            next = self.complete_l_string[end_index]
        return start_index,end_index
    def __check_segments_are_crossing(self, first_segment: List[Tuple[float, float]] ,
                                    second_segment: List[Tuple[float, float]]) -> bool:
        """
        Checks if the two segments given are crossing each other
        :param first_segment: start and end coordinates of first segment
        :param second_segment: start and end coordinates of second segment
        :return: true if they are crossing otherwise false
        """
        line_1 = LineString(first_segment)
        line_2 = LineString(second_segment)
        return line_1.intersects(line_2)


    def changeItemIndex(self, event):
        """Lädt die Bild-Datei zu der jeweiligen Iteration"""
        # initialisieren
        self.__initTurlteStartPos()
        self.loaded_bmp = None
        self.loaded_img = None
        filename = self.output[self.itera_cbox.get()]
        # prüfen ob ein Bild geladen wurde
        try:
            self.loaded_img = tk.PhotoImage(file=filename)
        except BaseException:
            showerror('File not found', 'File "' + filename + '" does not exist.')
            return
        self.drawframe.create_image((0, 0), image=self.loaded_img)
        self.drawframe.grid(row=0, column=0, columnspan=5)
        # funktion für GUI-Elemente - Ende

        # private funktionen werden mit mit "__" deklariert

    def __initTurlteStartPos(self):
        """Initialisiert den Turtle"""
        self.turtle.clear()
        self.turtle.hideturtle()
        self.turtle.penup()
        self.turtle.goto(0, -winHeight / 2)
        self.turtle.pendown()

    def __rule(self, sequence):
        """ Sucht in der gegebenen <sequence> nach der entsprechend zu ersetztenden Regel """
        if sequence in self.rules:
            return self.rules[sequence]
        return sequence

    def __cut_rule(self, sequence):
        """ Sucht in der gegebenen <sequence> nach der entsprechend zu ersetztenden Regel """
        if sequence in self.regrow_rules:
            return self.regrow_rules[sequence]
        return sequence

    def __derivation(self, derived, steps):
        """ Erzeugt mit der Regel für jeden Iterationsschritt einen Sequenz an Zeichenbefehlen """
        for _ in range(steps):
            next_seq = derived[-1]
            # Für jeden <char> in <next_seq> prüfe, ob die Regel angewendet werden muss
            next_axiom = [self.__rule(char) for char in next_seq]
            if self.cutted:
                next_axiom = [self.__cut_rule(char) for char in next_axiom]
            derived.append(''.join(next_axiom))
        return derived

    def __splitRule(self, input):
        """input muss "=" enthalten, z.B. "F=FF+[+F-F-F]-[-F+F+F]". F ist der Pattern der mit FF+[+F-F-F]-[-F+F+F] ersetzt wird"""
        x = input.split('=', 1)
        return {x[0]: x[1]}

    def __checkAxiomFormat(self, axiomStr):
        """Prüft ob der axiomStr richtig ist"""
        if len(axiomStr) == 0:
            showerror('Missing Entry', 'The "Axiom" must not be empty.')
            return False
        elif not axiomStr in ["F", "G", "R", "L"]:
            showerror('Wrong Entry', 'The axiom must be an element from ("F", "G", "R", "L").')
            return False
        else:
            return True

    def __checkAngleFormat(self, angleStr):
        """Fängt den Typenfehler ab und gibt entsprechend True zurück wenn kein Fehler kam"""
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
        """Fängt den alles was keine potive Ganzzahl ist ab und gibt entsprechend True zurück wenn kein Fehler kam"""
        if not iterationStr.isnumeric():
            showerror('Wrong Format', '"Iteration" must be a positive number.')
            return False
        else:
            return True

    def __checkRuleFormat(self, ruleStr):
        """Fängt Formatierungsfehler innerhalb des ruleStr ab"""
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
        """Sammelt die Stringlängen der einzelnen Iterationen"""
        posArr = []
        modelCount = len(model)
        for step in range(1, modelCount):
            posArr.append(len(model[step]) - 1)
        return posArr

    def __save_png(self):
        """Speichert das gezeichnete Bild in schwarz-weiß"""
        savename = "Output_LS_" + datetime.today().strftime('%Y-%m-%d_%H-%M-%S-%f') + extension
        ps = self.drawframe.postscript(colormode='mono', pagewidth=winWidth - 1, pageheight=winHeight - 1)
        img = Image.open(io.BytesIO(ps.encode('utf-8'))).convert(mode='1')
        img.save(savename)
        return savename

    def __fill_combobox(self, maxiteration, files):
        """Füllt die ComboBox mit Daten zum auswählen der Iterationsschritte"""
        self.output.clear()
        self.itera_cbox['state'] = 'readonly'
        self.itera_cbox['values'] = []
        cbItems = []
        for i in range(0, maxiteration):
            cbItems.append('Iteration ' + str(i + 1))
        self.itera_cbox['values'] = cbItems
        for i in range(0, len(cbItems)):
            self.output[cbItems[i]] = files[i]
            # private funktionen - Ende

    # public funktionen
    def draw_l_system(self):
        """ Zeichenroutine des L-Systems """
        self.isstopped = False
        seg_length = 5
        alpha_zero = 90

        if (not self.cutted):
            self.rules = self.__splitRule(self.rule.get())
            axiom = self.axiom.get()
            iterations = int(self.iteration.get())
            self.angle_value = float(self.angle.get())
            self.model = [axiom]
        else:
            self.regrow_rules = self.__splitRule(self.regrow_rule.get().lower())
            #self.cutted_string[self.cutted_branch_index] = "["+self.regrow_axiom.get().lower()
            iterations = int(self.regrow_iterations.get())
            savename=self.__save_png()
            self.model_cut_images.append(savename)
            self.model.append(self.cutted_string)
            self.model_indices_of_cuts.append(len(self.model) - 1)
        self.model = self.__derivation(self.model, iterations)
        self.turtle.speed(0)  # (0 = am schnellsten)
        self.turtle.setheading(alpha_zero)  # Richtung des Turtles initialisieren  
        stack = []
        # speichert die Dateinamen
        outputfiles = []
        # Zähler für Prozentanzeige
        count = 0
        maxCount = len(self.model[-1])
        # suchen nach den Iterationspunkten
        steps = self.__countModels(self.model)
        # Bei der Regel "F=F" bleibt über mehrere Iterationen das Ergebnis gleich
        if max(steps) == min(steps):
            iterations = 1
        # iteriere durch den letzten String
        self.coordinates = []
        self.complete_l_string = self.model[-1]
        for command in self.model[-1]:
            if self.isstopped:
                break
            self.turtle.pd()
            if command in ["F", "G", "R", "L","f","g","r","l"]:
                if command in ["F", "G", "R", "L"]:
                    self.turtle.pencolor("black")
                if command in ["f","g","r","l"]:
                    self.turtle.pencolor("blue")
                start_coordinate = self.turtle.pos()
                self.turtle.forward(seg_length)
                end_coordinate = self.turtle.pos()
                self.coordinates.append([start_coordinate, end_coordinate])
            # elif command == "f":
            #     self.turtle.pu()  # pen up - not drawing
            #     self.turtle.forward(seg_length)
            elif command == "+":
                self.turtle.left(self.angle_value)
            elif command == "-":
                self.turtle.right(self.angle_value)
            elif command == "[":
                stack.append((self.turtle.position(), self.turtle.heading()))
            elif command == "]":
                self.turtle.pu()  # pen up - not drawing
                position, heading = stack.pop()
                self.turtle.goto(position)
                self.turtle.setheading(heading)
            if command not in ["F", "G", "R", "L","f","g","r","l"]:
                self.coordinates.append([(0, 0), (0, 0)])
            # einzelnen Bilder pro Iteration speichern
            if count in steps:
                savename = self.__save_png()
                outputfiles.append(savename)
            percent = count / maxCount * 100
            title = "Lindenmayer-System ," + str(round(percent, 1)) + "% gezeichnet..."
            self.master.title(title)
            count = count + 1
        self.master.title("Lindenmayer-System")
        self.__fill_combobox(iterations, outputfiles)
        self.isstopped = False
        self.resetBtn['state'] = 'normal'
        self.cutBtn['state'] = 'normal'
        if self.cutted:
            self.resetcutBtn['state'] = 'normal'
    # public funktionen - End


if __name__ == "__main__":
    # Standart-Fenster erzeugen
    root = tk.Tk()
    # App und Fenster mit passenden Eigenschaft befüllen
    app = App(root)
    # App Loop um auf Button drücke zu reagieren
    root.mainloop()
