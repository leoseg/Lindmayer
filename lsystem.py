import tkinter as tk
from tkinter import ttk
from lturtle import Lturtle
from utils import splitRule, derivation
from utils_cutting import *
import turtle
from format_checks import *
from copy import deepcopy
#Install with conda with 'conda env create -f env.yml'

# Size of window
winHeight = 480
winWidth = 600
extension = '.png'



class App:
    """
    Main class which creates the app
    """

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
        #self.regrow_axiom = tk.StringVar()
        self.regrow_rule = tk.StringVar()
        self.regrow_iterations = tk.StringVar()

        # Elements of GUI
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

        self.resetcutBtn = ttk.Button(master, text="Reset Cut", state=tk.DISABLED, command=lambda: self.pressresetcut())
        self.resetcutBtn.grid(row=4,column=3, columnspan=2,sticky=tk.E, padx=3)

        # Variables to save rules
        self.rules = {}
        self.regrow_rules = {}

        # Stores lindenmayer model
        self.model=[]

        # Set if its the firstcut
        self.firstcut = True

        # Screen for drawing turtles
        self.screen = turtle.TurtleScreen(self.drawframe)

        # Creates turtle for drawing simulation
        self.turtle = Lturtle(canvas=self.screen,master=master)
        self.screen.delay(0)

        # Creates turtle for cutting line
        self.cut_line_turtle = Lturtle(canvas=self.screen,master=master)

        # Creates turtle for redraw choosen iteration
        self.redraw_turtle = Lturtle(canvas=self.screen,master=master)


        #startvalues
        self.ruleEdit.insert(0,"F=FF-[-F+F+F]+ [+F-F+F]")
        self.angleEdit.insert(0,"22.5")
        self.axiomEdit.insert(0,"F")
        self.iterationEdit.insert(0,2)



    def pressgrow(self):
        """
        Command of the grow button,checks the given rules if they ok draws the lsystem
        :return:
        """
        candraw = False
        # Check if rules are in correct format
        axiomOk = checkAxiomFormat(self.axiomEdit.get())
        ruleformatOk = checkRuleFormat(self.ruleEdit.get())
        iterationOk = checkIterationFormat(self.iterationEdit.get())
        angleOk = checkAngleFormat(self.angleEdit.get())
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
        self.resetcutBtn['state'] = 'disabled'
        self.__toggle_grow_edits_state("normal")


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
                self.__cut_plant()
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
        ruleformatOk = checkRuleFormat(self.regrow_rule.get())
        iterationformatOk = checkIterationFormat(self.regrow_iterations.get())
        if ruleformatOk and iterationformatOk:
            self.popup.destroy()
            self.click = 0


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

        self.popup = tk.Toplevel(self.master)
        self.regrow_entry = ttk.Entry(self.popup, width=41, textvariable=self.regrow_rule)
        #self.regrow_axiom_entry = ttk.Entry(self.popup,width=41,textvariable=self.regrow_axiom)
        self.regrow_iterations_entry = ttk.Entry(self.popup,width=41,textvariable=self.regrow_iterations)
        self.regrow_confirm = ttk.Button(self.popup, text="Confirm", width=15, state=tk.NORMAL,
                                         command=lambda: self.pressconfirm())
        self.cancel = ttk.Button(self.popup,text="Cancel",width=15, state=tk.NORMAL,
                                         command=lambda: self.presscancel())

        self.iterationlabel = ttk.Label(self.popup, text="Iterations:")
        self.axiomlabel = ttk.Label(self.popup, text=f"Cutted branch char was: {self.axiom.get()}")
        self.ruleslabel = ttk.Label(self.popup, text="Rule:")


        # opens window
        self.axiomlabel.pack()
        self.ruleslabel.pack()
        self.regrow_entry.pack()
        self.iterationlabel.pack()
        self.regrow_iterations_entry.pack()
        self.regrow_confirm.pack()
        self.cancel.pack()


        # sets startdata
        if self.firstcut:
            self.regrow_entry.insert(0,"F=FF-[-F+F]+[-F+F]")
            self.regrow_iterations_entry.insert(0,1)
            self.firstcut = False


    def presscut(self):
        """
        If cut button is clicked sets function for click on screen
        :return:
        """
        self.cut_line = []
        self.click_num = 0

        self.screen.onclick(self.click_fun)


    def __cut_plant(self):
        """
        Cuts the plant at the nearest branch to the intersection point of the cutting line by removing the
        corresponding chars in the string and coordinates
        :param coordinates_cutting_line: start and end coordinates of the cutting line
        :return:
        """

        self.tribe_cutted = check_if_tribe_cutted(self.complete_l_string,self.cutting_index)
        if self.tribe_cutted:
            #self.coordinates = self.coordinates[:self.cutting_index]
            self.cutted_string = self.complete_l_string[:self.cutting_index]
        else:
            self.end_index = get_end_index(self.cutting_index,self.complete_l_string)
            #self.coordinates = self.coordinates[:self.cutting_index] + self.coordinates[self.end_index :]
            self.cutted_string = self.complete_l_string[:self.cutting_index] + self.complete_l_string[self.end_index :]



    def changeItemIndex(self, event):
        """
        Loads the image file for the given iteration selected
        :param event:
        :return:
        """
        # initialize
        self.turtle.reset_turtle()
        self.redraw_turtle.reset_turtle()
        self.cut_line_turtle.reset_turtle()
        m = re.search(r"\d", self.itera_cbox.get())
        self.choosen_iteration = int(self.itera_cbox.get()[m.start()])

        sequence = self.model[self.choosen_iteration]
        self.coordinates = self.turtle.draw_sequence(sequence,self.angle_value)
        self.complete_l_string = sequence


    def pressresetcut(self):
        """
        Resets the cut
        :return:
        """
        self.turtle.reset_turtle()
        self.redraw_turtle.reset_turtle()
        self.cut_line_turtle.reset_turtle()
        self.coordinates = self.turtle.draw_sequence(self.complete_string_before_cut, self.angle_value)
        self.model =deepcopy( self.models_before_cut)
        self.cutBtn['state'] = 'normal'
        self.itera_cbox.set(f"Iteration {self.old_iterations}")
        self.changeItemIndex(None)
        self.__fill_combobox(self.old_iterations)


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

        self.itera_cbox['state'] = 'readonly'
        self.itera_cbox['values'] = []
        cbItems = []
        for i in range(0, maxiteration):
            cbItems.append('Iteration ' + str(i + 1))
        self.itera_cbox['values'] = cbItems


    def __toggle_grow_edits_state(self,state:str):
        """
        Sets the states of the edits for growing the plant in the first place
        :param state: state to edit
        :return:
        """
        self.ruleEdit['state'] = state
        self.angleEdit['state'] = state
        self.axiomEdit['state'] = state
        self.iterationEdit['state'] = state
    def draw_l_system(self):
        """
        Draws the l-system
        :return:
        """

        # gets user values (angel, rule,axiom)
        self.resetBtn['state'] = 'normal'
        self.rules = splitRule(self.rule.get())
        axiom = self.axiom.get()
        iterations = int(self.iteration.get())
        self.angle_value = float(self.angle.get())

        # derivates models
        self.model = [axiom]
        self.model = derivation(self.model, iterations, self.rules)
        self.complete_l_string = self.model[-1]
        self.complete_string_before_cut = deepcopy(self.model[-1])
        self.models_before_cut = deepcopy(self.model)

        #draw system and saves coodirnates
        self.coordinates= self.turtle.draw_sequence(self.model[-1], self.angle_value, True, True)
        self.master.title("Lindenmayer-System")
        self.__fill_combobox(iterations)
        self.old_iterations =iterations

        # enables buttons
        self.cutBtn['state'] = 'normal'

        self.choosen_iteration=len(self.model) -1
        self.__toggle_grow_edits_state("disabled")
    # public funktionen - End
    def draw_after_cut(self):
        """
        Draws the l-system after the cut
        :return:
        """
        # derivates regrow models
        self.regrow_rules = splitRule(self.regrow_rule.get().lower())
        iterations = int(self.regrow_iterations.get())
        regrow_model = derivation([self.complete_l_string[self.cutting_index].lower()], iterations, self.regrow_rules)

        # derivates models
        self.model = derivation(self.model, iterations, self.rules)
        self.__insert_regrow_model_into_model(regrow_model)
        #draws new system with cutted branch
        self.turtle.draw_sequence(self.model[-1], self.angle_value, True, True)
        self.master.title("Lindenmayer-System")
        self.__fill_combobox(iterations + self.old_iterations)

        # enables buttons
        self.resetBtn['state'] = 'normal'
        self.cutBtn['state'] = 'disabled'
        self.resetcutBtn['state'] = 'normal'

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


if __name__ == "__main__":
    # Standart-Fenster erzeugen
    root = tk.Tk()
    # App und Fenster mit passenden Eigenschaft befüllen
    app = App(root)
    # App Loop um auf Button drücke zu reagieren
    root.mainloop()
