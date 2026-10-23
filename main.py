import tkinter as tk
import sys
import subprocess
import json
import os

try:
    import keyboard
except ImportError:
    print("Keyboard n existe, vou baixar pra vc :)")
    subprocess.check_call([sys.executable,"-m","pip","install","keyboard"])
    import keyboard

class ContadorApp():
    def __init__(self,root):

        self.corTexto = "#cdd6f4"
        self.corFundo = "#1e1e2e"
        self.corDestaque = "#89b4fa"
        self.corSubt = "#7f849c"

        self.Root = root
        self.Root.title("Contador")
        self.Root.config(bg=self.corFundo)
        self.AddSpins = True
        self.add = ""
        self.spinBreak = 4
        self.spinPres = True
        self.arquivoSalvamento = "contador_prestiges.json"
        self.contador,self.spins = self.carregarContador()
        self.Root.attributes("-topmost",True)

        self.Root.geometry("200x320")

        self.label_spinbreak = tk.Label(
            self.Root,
            font=("Arial",14,"bold"),
            fg=self.corTexto,
            bg=self.corFundo
        )
        self.label_spinbreak.pack()
        
        self.canvas_bolas = tk.Canvas(self.Root,width=160,height=30,highlightthickness=0,bg=self.corFundo)
        self.canvas_bolas.pack()

        self.AtualizarBolas()

        self.label_titulos = tk.Label(
            self.Root,
            text="Prestiges",
            font=("Arial",14,"bold"),
            bg = self.corFundo,
            fg=self.corTexto
        )
        self.label_titulos.pack(pady=(5,0))
        
        self.label_contador = tk.Label(
            self.Root,
            text=str(self.contador),
            font=("Arial",30,"bold"),
            bg=self.corFundo,
            fg = self.corDestaque
        )
        self.label_contador.pack(pady=(15,0))

        self.label_spintitulo = tk.Label(      
            self.Root,
            text="Spins:",
            font=("Arial",14,"bold"),
            fg=self.corTexto,
            bg=self.corFundo)
        self.label_spintitulo.pack(pady=(15,0))

        self.label_spincount = tk.Label(
            self.Root,
            text="...",
            font=("Arial",10,"bold"),
            fg=self.corSubt,
            bg = self.corFundo
        )

        self.label_spincount.pack(pady=(10))

        self.label_spins = tk.Label(
            self.Root,
            text=str(self.spins),
            font=("Arial",30,"bold"),
            fg=self.corDestaque,
            bg=self.corFundo
        )
        self.label_spins.pack(pady=(10,0))
        keyboard.on_press_key("delete",lambda _:self.Root.after(0,self.IncrementarSpins))
        keyboard.on_press_key(76, lambda _: self.Root.after(0,self.incrementar))
        keyboard.on_press_key(82,lambda _: self.Root.after(0,self.Diminuir))
        keyboard.on_press_key("enter",lambda _: self.ConfirmarSpins())
        keyboard.on_press(self.PegarDigitos)
        keyboard.on_press_key("+",lambda _: self.Root.after(0,self.SpinPres()))
        
    def carregarContador(self):
        if os.path.exists(self.arquivoSalvamento):
            try:
                with open(self.arquivoSalvamento,"r") as f:
                    dados = json.load(f)
                    return dados.get("prestiges",0),dados.get("spins",0)
            except (json.JSONDecodeError,ValueError):
                return 0,0
        return 0,0

    def IncrementarSpins(self):
        if self.AddSpins:
            self.AddSpins = False
            self.add = ""
        else:
            self.AddSpins = True
            self.add=""
            self.label_spincount.config(text=str("..."))

    def PegarDigitos(self,tecla):
        if not self.AddSpins:
            teclas = ["0","1","2","3","4","5","6","7","8","9","-"]
            if tecla.name in teclas:
                self.add = self.add+tecla.name
            elif tecla.name == "backspace":
                self.add = self.add[:-1]
            self.label_spincount.config(text=str(self.add))
        else:
            if self.add != "":
                self.spins += int(self.add)
                self.label_spins.config(text=str(self.spins))
                self.add =""
            
    def ConfirmarSpins(self):
        if not self.AddSpins:
            if self.add != "":
                self.spins +=int(self.add)
                self.label_spins.config(text=str(self.spins))
                self.salvar_contador()
        self.add = ""
        self.label_spincount.config(text="...")
        self.AddSpins = True

    def salvar_contador(self):
        dados = {
            "prestiges":self.contador,
            "spins":self.spins
        }
        with open(self.arquivoSalvamento,"w") as f:
            json.dump(dados,f,indent=4)

    def incrementar(self):
        if self.AddSpins:
            self.contador +=1
            self.label_contador.config(text=str(self.contador))
            self.salvar_contador()
            self.SpinBreak(1)

    def Diminuir(self):
        if self.AddSpins:
            self.contador -=1
            self.label_contador.config(text=str(self.contador))
            self.salvar_contador()
            self.SpinBreak(-1)

    def SpinBreak(self,qnt):
        if self.spinPres:
            self.spinBreak += qnt
            if self.spinBreak > 4:
                self.spinBreak = 1
            if self.spinBreak < 1:
                self.spinBreak = 4
        self.AtualizarBolas()

    def SpinPres(self):
        self.spinPres = not self.spinPres
        self.AtualizarBolas()

    def AtualizarBolas(self):
        self.canvas_bolas.delete("all")
        raio = 8
        espacamento = 35
        x = 25
        y = 15
        cor = self.corDestaque
        for i in range(4):
            x1 = x + (i*espacamento) - raio
            x2 = x + (i*espacamento) + raio

            y1 = y - raio
            y2 = y + raio

            if i < self.spinBreak:
                cor = self.corDestaque
            else:
                cor = ""
            if self.spinPres:
                texto = f"Spinbreak in: {4-self.spinBreak}"
            else:
                texto = "Disabled"
                cor = "red"
            self.canvas_bolas.create_oval(x1,y1,x2,y2,fill=cor,outline=self.corSubt)

        self.label_spinbreak.config(text=f"{texto}")


root = tk.Tk()
app = ContadorApp(root)
root.mainloop()