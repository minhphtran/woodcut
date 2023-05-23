import tkinter as tk
from tkinter import font
from pulp import *
import numpy as np


required_lengths = [40, 36.4, 34, 17.6]
frequencies = [11, 6, 2, 2]
cut_width = .5

woods = []; num_pieces = [];
result_rows = []

class App:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
  
        # Creating a Font object of "TkDefaultFont"
        self.defaultFont = font.nametofont("TkDefaultFont")
  
        # Overriding default-font with custom settings
        # i.e changing font-family, size and weight
        self.defaultFont.configure(family="muli",
                                   size = 15,
                                   weight=font.BOLD)
  
  
def callback(P):
    if str.isdigit(P) or P == "":
        return True
    else:
        return False
    
def optim_cut(woods, num_pieces, required_lengths, frequencies, cut_width):
    pieces = [("piece{}.{}".format(woods[i], j), woods[i]) for i in range(len(woods)) for j in range(num_pieces[i])]
    lens = [f'len{l}' for l in required_lengths]
    
    pieces_var = [dict(
        val = p[1], 
        len_var = pulp.LpVariable.dicts(p[0], lens, lowBound = 0, cat = "Integer"),
        leftover_var = LpVariable(f"{p[0]}_leftover", lowBound = 0, cat = "Continuous")
    )  for p in pieces]
    n = LpVariable("n", lowBound = 0, cat = "Integer")
    leftover_max = LpVariable("leftover_max", lowBound = 0, upBound = max(woods), cat = "Continuous")
    
    prob = LpProblem("wood_cut", LpMaximize)
    prob += lpSum([10e3 * n, leftover_max]) 
    
    for p in pieces_var:
        prob += lpSum([i * (j + cut_width) for i, j in zip(p['len_var'].values(), required_lengths)] +
                    p['leftover_var']
                   ) == p['val']
        prob += lpSum([p['leftover_var'], -leftover_max]) >= 0
    
    for l, f in zip(lens, frequencies):
        prob += lpSum([f * n] + [-p['len_var'][l] for p in pieces_var])  <= 0
        
    prob.solve(CPLEX_PY())
    return (pieces_var, int(n.varValue))

        
def add_fields():
    new_wood = int(e1.get())
    if new_wood not in woods:
        woods.append(new_wood)
        num_pieces.append(int(e2.get()))
    else:
        idx = woods.index(new_wood)
        num_pieces[idx] = num_pieces[idx] + int(e2.get())
    mats['text'] = "; ".join([f"{j} x {i}cm" for i, j in zip(woods, num_pieces)])

def remove_fields():
    remove_wood = int(e1.get())
    if remove_wood in woods:
        idx = woods.index(remove_wood)
        new_num = max(0, num_pieces[idx] - int(e2.get()))
        num_pieces[idx] = new_num
        mats['text'] = "; ".join([f"{j} x {i}cm" for i, j in zip(woods, num_pieces)])


    
def delete_row():
    for rowno, row in reversed(list(enumerate(result_rows))):
        for i in row:
            i.destroy()
        result_rows.pop(rowno)
            
def reset_fields():
    woods = []
    num_pieces = []
    mats['text'] = "none added"
    delete_row()

def solve_cut():
    delete_row()
    (pieces_res, n_res) = optim_cut(woods, num_pieces, required_lengths, frequencies, cut_width)
    
    title_res = tk.Label(master, text = "result: ")
    title_res.grid(row = 9, column = 0)
    n_show = tk.Label(master, text = f"generate {n_res} pieces")
    n_show.grid(row = 9, column = 1)
    result_rows.append([title_res, n_show])
    
    row_start = 10
    for i in range(len(pieces_res)):
        items = []
        p = pieces_res[i]
        
        label_text = "{}cm-length piece: ".format(p['val'])
        t = tk.Label(master, text = "{}cm-length piece: ".format(p['val']), font = 'muli')
        t.grid(row = row_start + i, column = 0)
        items.append(t)   
        
        res_text = '; '.join(["{} x {}cm".format(int(j.varValue), i[3:])
                                       for i,j in p['len_var'].items() if j.varValue > 0])
        res_text = "none " if res_text == "" else res_text
        res_text = res_text+ " ({}cm left)".format(p['leftover_var'].varValue)
        b = tk.Label(master, 
                     text = res_text, 
                     font = 'muli')
        b.grid(row = row_start + i, column = 1)

        print(label_text + res_text)
        items.append(b)
        
        result_rows.append(items)

if __name__ == "__main__":
    master = tk.Tk()
    vcmd = (master.register(callback))
    


    tk.Label(master, text = "current setting:").grid(row = 0)
    tk.Label(master, 
             text = "     ".join([f"cut width = {cut_width}cm"] + 
                                 [f"{j} x {i}cm" for i, j in zip(required_lengths, frequencies)]
                                ),
             font = ("muli")). grid(row = 1)
        
    tk.Label(master, 
             text = "length").grid(row = 3)
    tk.Label(master, 
             text = "no. piecies").grid(row = 4)

    e1 = tk.Entry(master, validate = 'all', validatecommand = (vcmd, '%P'))
    e2 = tk.Entry(master, validate = 'all', validatecommand = (vcmd, '%P'))

    e1.grid(row = 3, column = 1)
    e2.grid(row = 4, column = 1)

    mat_title = tk.Label(master, text = "materials:").grid(row = 7, column = 0)
    mats = tk.Label(master, text = "none added", font = ("muli"))
    mats.grid(row = 7, column = 1)
    
    
    but1 = tk.Button(master, 
              text = 'add', command = add_fields).grid(row = 6,
                                                     column = 1, 
                                                     sticky = tk.W, 
                                                     pady = 2)
    
    but5 = tk.Button(master, 
              text = 'remove', command = remove_fields).grid(row = 6,
                                                         column = 2, 
                                                         sticky = tk.W, 
                                                         pady = 0)
    
    
    but2 = tk.Button(master, 
              text = 'calculate', command = solve_cut).grid(row = 6,
                                                             column = 0, 
                                                             sticky = tk.W, 
                                                             pady = 2)
    
    but3 = tk.Button(master, 
              text = 'reset', command = reset_fields).grid(row = 6,
                                   column = 3, 
                                   sticky = tk.W, 
                                   pady = 2)
    but4 = tk.Button(master, 
              text = 'quit', 
              command = master.quit).grid(row = 6, 
                                          column = 4, 
                                          sticky = tk.W, 
                                          pady = 2)
    
    
    
  
    app = App(master)
    master.mainloop()
