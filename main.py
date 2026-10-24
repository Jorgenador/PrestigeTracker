import tkinter as tk
import sys
import subprocess
import json
import os

try:
    import keyboard
except ImportError:
    print("a library keyboard n existe, vou baixar pra vc :)")
    subprocess.check_call([sys.executable,"-m","pip","install","keyboard"])
    import keyboard

class ContadorApp():
    def __init__(self,root):

        self.corTexto = "#cdd6f4"
        self.corFundo = "#1e1e2e"
        self.corDestaque = "#89b4fa"
        self.corSubt = "#7f849c"

        self.tempoSegundos = 0
        self.totalTempo = 0

        self.Pausado = True
        self.estatisticasJ = False
        self.Root = root
        self.Root.title("")
        self.Root.config(bg=self.corFundo)
        self.AddSpins = True
        self.add = ""
        self.spinBreak = 0
        self.spinPres = True
        self.arquivoSalvamento = "contador_prestiges.json"
        self.ciclosSessao = 0
        self.contador,self.spins,self.ciclos,self.totalTempo = self.carregarContador()
        self.Root.attributes("-topmost",True)
        self.Root.protocol("WM_DELETE_WINDOW",self.fecharSalvar)
        self.Root.geometry("200x350")

        self.frameP = tk.Frame(self.Root)
        self.frameP.pack(fill="both",expand=True)
        self.frameP.config(bg=self.corFundo)
        
        self.label_spinbreak = tk.Label(
            self.frameP,
            font=("Arial",14,"bold"),
            fg=self.corTexto,
            bg=self.corFundo
        )
        self.label_spinbreak.pack(pady=(10,0))
        
        self.canvas_bolas = tk.Canvas(self.frameP,width=160,height=30,highlightthickness=0,bg=self.corFundo)
        self.canvas_bolas.pack()

        self.frameE = tk.Frame(self.Root)
        self.frameE.config(bg=self.corFundo)

        self.label_stats = tk.Label(
            self.frameE,
            text="Stats",
            font=("Arial",30,"bold"),
            bg=self.corFundo,
            fg=self.corTexto
        )
        self.label_stats.pack(pady=(10,0))

        self.label_statCycle = tk.Label(
            self.frameE,
            text=f"This session cycles: {self.ciclosSessao}",
            font=("Arial",10,"bold"),
            bg=self.corFundo,
            fg=self.corTexto,
        )
        self.label_statCycle.pack(pady=(10,0))
        self.label_statsTCycle = tk.Label(
             
            self.frameE,
            text=f"Total cycles: {self.ciclos}",
            font=("Arial",10,"bold"),
            bg=self.corFundo,
            fg=self.corTexto,
        )
        self.label_statsTCycle.pack(pady=(5,0))

        self.label_statSTime = tk.Label(
            self.frameE,
            text=f"This sesion time: 00:00:00",
            font=("Arial",10,"bold"),
            bg=self.corFundo,
            fg=self.corTexto           
        )
        self.label_statSTime.pack(pady=(5,0))

        self.label_statsTTime = tk.Label(
            self.frameE,
            text=f"Total Time: 00:00:00",
            font=("Arial",10,"bold"),
            bg=self.corFundo,
            fg=self.corTexto,
        )
        self.label_statsTTime.pack(pady=(5,0))


        self.label_statsEstK= tk.Label(
            self.frameE,
            text=f"Estimated Kills: {self.contador*2}",
            font=("Arial",10,"bold"),
            bg=self.corFundo,
            fg=self.corTexto           
        )
        self.label_statsEstK.pack(pady=(5,0))
        
        self.label_titulos = tk.Label(
            self.frameP,
            text="Prestiges",
            font=("Arial",14,"bold"),
            bg = self.corFundo,
            fg=self.corTexto
        )
        self.label_titulos.pack(pady=(10,0))
        
        self.label_contador = tk.Label(
            self.frameP,
            text=str(self.contador),
            font=("Arial",30,"bold"),
            bg=self.corFundo,
            fg = self.corDestaque
        )
        self.label_contador.pack(pady=(10,0))

        self.label_spintitulo = tk.Label(      
            self.frameP,
            text="Spins:",
            font=("Arial",14,"bold"),
            fg=self.corTexto,
            bg=self.corFundo)
        self.label_spintitulo.pack(pady=(10,0))

        self.label_spincount = tk.Label(
            self.frameP,
            text="...",
            font=("Arial",10,"bold"),
            fg=self.corSubt,
            bg = self.corFundo
        )

        self.label_spincount.pack(pady=(10))

        self.label_spins = tk.Label(
            self.frameP,
            text=str(self.spins),
            font=("Arial",30,"bold"),
            fg=self.corDestaque,
            bg=self.corFundo
        )
        self.label_spins.pack(pady=(10,0))

        self.frame_info = tk.Frame(self.frameP)
        self.frame_info.pack(pady=(15,0))

        self.label_ciclos = tk.Label(
            self.frame_info,
            text=f"Cycles: {self.ciclosSessao}",
            font=("Arial",10,"bold"),
            fg=self.corSubt,
            bg=self.corFundo
        )

        self.label_ciclos.grid(row=0,column=0,sticky="w")

        self.label_tempo = tk.Label(
            self.frame_info,
            text=f"Time: 00:00:00",
            font=("Arial",10,"bold"),
            bg=self.corFundo,
            fg=self.corSubt
                )

        self.label_tempo.grid(row=0,column=1,sticky="w")

        keyboard.on_press_key("delete",lambda _:self.Root.after(0,self.IncrementarSpins))
        keyboard.on_press_key(76, lambda _: self.Root.after(0,self.incrementar))
        keyboard.on_press_key(82,lambda _: self.Root.after(0,self.Diminuir))
        keyboard.on_press_key("enter",lambda _: self.Root.after(0,self.ConfirmarSpins))
        keyboard.on_press(lambda e: self.Root.after(0,self.PegarDigitos,e))
        keyboard.on_press_key("+",lambda _: self.Root.after(0,self.SpinPres))
        keyboard.on_press_key("-",lambda _: self.Root.after(0,self.Pausar))
        keyboard.on_press_key("*",lambda _: self.Root.after(0,self.trocarJanela))
        
        self.AtualizarBolas()
        self.atualizarTimer()
        
    def carregarContador(self):
        if os.path.exists(self.arquivoSalvamento):
            try:
                with open(self.arquivoSalvamento,"r") as f:
                    dados = json.load(f)
                    return dados.get("prestiges",0),dados.get("spins",0),dados.get("ciclos",0),dados.get("tempo",0)
            except (json.JSONDecodeError,ValueError):
                return 0,0,0,0
        return 0,0,0,0

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
            if tecla.name == "-":
                if self.add == "":
                    self.add = "-"
            elif tecla.name in teclas:
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
            "spins":self.spins,
            "ciclos":self.ciclos,
            "tempo":self.totalTempo
        }
        with open(self.arquivoSalvamento,"w") as f:
            json.dump(dados,f,indent=4)

    def incrementar(self):
        if self.AddSpins:
            self.contador +=1
            self.label_contador.config(text=str(self.contador))
            self.label_statsEstK.config(text=f"Estimated Kills: {self.contador*2}")
            self.salvar_contador()
            self.SpinBreak(1)

    def Diminuir(self):
        if self.AddSpins:
            self.contador -=1
            self.label_contador.config(text=str(self.contador))
            self.label_statsEstK.config(text=f"Estimated Kills: {self.contador*2}")
            self.salvar_contador()
            self.SpinBreak(-1)

    def SpinBreak(self,qnt):
        if self.spinPres:
            self.spinBreak += qnt
            if self.spinBreak > 4:
                self.attCiclos(True)
                self.spinBreak = 1
            if self.spinBreak < 1:
                self.attCiclos(False)
                self.spinBreak = 4
        self.AtualizarBolas()

    def attCiclos(self,situacao):
        if situacao:
            self.ciclos+=1
            self.ciclosSessao+=1
        else:
            if self.ciclos > 0:
                self.ciclos-=1
                self.ciclosSessao-=1
        self.label_ciclos.config(text=f"Cycles: {self.ciclosSessao}")
        self.label_statCycle.config(text=f"This session cycles: {self.ciclosSessao}")
        self.label_statsTCycle.config(text=f"Total cycles: {self.ciclos}")
        self.salvar_contador()

    def SpinPres(self):
        self.spinPres = not self.spinPres
        self.AtualizarBolas()

    def AtualizarBolas(self):
        self.canvas_bolas.delete("all")
        raio = 8
        espacamento = 35
        x = 25
        y = 15
        cor = ""
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

    def atualizarTimer(self):
        if self.AddSpins and not self.Pausado:
            self.label_tempo.config(fg=self.corSubt)
            self.label_statsTTime.config(fg=self.corTexto)
            self.label_statSTime.config(fg=self.corTexto)
            self.tempoSegundos+=1
            self.totalTempo+=1
        else:
            self.label_tempo.config(fg="red")
            self.label_statsTTime.config(fg="red")
            self.label_statSTime.config(fg="red")

        horas = self.tempoSegundos//3600
        min = (self.tempoSegundos%3600)//60
        sec = self.tempoSegundos % 60

        horas2 = self.totalTempo//3600
        min2 = (self.totalTempo%3600)//60
        sec2 = self.totalTempo % 60

        tempo_formatado = f"Session: {horas:02d}:{min:02d}:{sec:02d}"
        tempoFormatado2 = f"Total Time: {horas2:02d}:{min2:02d}:{sec2:02d}"

        
        self.label_tempo.config(text=tempo_formatado)
        self.label_statSTime.config(text=tempo_formatado)
        self.label_statsTTime.config(text=tempoFormatado2)
        self.Root.after(1000,self.atualizarTimer)

    def Pausar(self):
        if self.AddSpins:
            self.Pausado = not self.Pausado

    def trocarJanela(self):
        if self.estatisticasJ:
            self.frameE.pack_forget()
            self.frameP.pack(fill="both",expand=True)
            self.estatisticasJ = False
        else:
            self.frameP.pack_forget()
            self.frameE.pack(fill="both",expand=True)
            self.estatisticasJ = True

    def fecharSalvar(self):
        self.salvar_contador()
        print("Salvo antes de fechar!!")
        self.Root.destroy()
        

root = tk.Tk()
app = ContadorApp(root)
root.mainloop()