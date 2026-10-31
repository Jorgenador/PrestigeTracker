import tkinter as tk
import sys
import subprocess
import json
import os
import time

try:
    import keyboard
    import cv2
    from mss import MSS
    import rapidocr
    import numpy as np
    from rapidocr import RapidOCR
except ImportError:
    print("a library keyboard n existe, vou baixar pra vc :)")
    subprocess.check_call([sys.executable,"py","-m","pip","install","-r","requirements" ])
    import keyboard
    import cv2
    from mss import MSS
    import rapidocr
    import numpy as np
    from rapidocr import RapidOCR

class ContadorApp():
    def __init__(self,root):

        self.corTexto = "#cdd6f4"
        self.corFundo = "#1e1e2e"
        self.corDestaque = "#89b4fa"
        self.corSubt = "#7f849c"
        self.acuracia = 0.7
        self.sct = MSS()
        self.tempoSegundos = 0
        self.totalTempo = 0
        self.template = None
        self.template2 = None
        self.PresCd = 0
        self.templates = {}
        self.tick = 0
        self.prestigioVisivel = False
        self.timerVisivel = False
        self.MaxP = 3
        self.Pausado = False
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
        self.ocr = RapidOCR()
        self.leituraPendente = False
        self.framesMenu = 0

        self.contador,self.spins,self.ciclos,self.totalTempo,self.regioes = self.carregarContador()
        for nome in self.regioes:
            caminho = self.caminhoDe(nome)
            if os.path.exists(caminho):
                self.templates[nome] = cv2.imread(caminho,cv2.IMREAD_GRAYSCALE)


        self.Root.attributes("-topmost",True)
        self.Root.protocol("WM_DELETE_WINDOW",self.fecharSalvar)
        self.Root.overrideredirect(True)
        largura = 200
        altura = 374
        x = self.Root.winfo_screenwidth() - largura - 200
        y = 10
        self.Root.geometry(f"{largura}x{altura}+{x}+{y}")

        self.barra = tk.Frame(
            self.Root,
            bg=self.corFundo
        )
        self.barra.pack(fill="x",side="top")


        self.textBarra = tk.Label(
            self.barra,
            font=("Arial",10,"bold"),
            bg=self.corFundo,
            fg=self.corTexto,
            text="Prestige Tracker"
        )

        self.textBarra.pack(side="left",padx=(5,0),pady=(0,0))

        self.but_fechar = tk.Button(
            self.barra,
            text="X",
            bg=self.corFundo,
            fg=self.corTexto,
            bd=0,
            width=3,
            activebackground="#f38ba8",
            activeforeground=self.corFundo,
            command=self.fecharSalvar
        )
        self.but_fechar.pack(side="right")

        self.barra.bind("<Button-1>",self.iniciarArrastar)
        self.barra.bind("<B1-Motion>",self.arrastar)
        
        self.textBarra.bind("<Button-1>",self.iniciarArrastar)
        self.textBarra.bind("<B1-Motion>",self.arrastar)
                


        self.but_fechar.bind("<Enter>",lambda e: self.but_fechar.config(bg="#f38ba8"))
        self.but_fechar.bind("<Leave>",lambda e:self.but_fechar.config(bg=self.corFundo))

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
            text=f"Session cycles: {self.ciclosSessao}",
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
        keyboard.on_press_key("f8",lambda _:self.Root.after(0,self.capturarTemplate,"prestigio"))
        keyboard.on_press_key("f7",lambda _:self.Root.after(0,self.capturarTemplate,"timer"))
        keyboard.on_press_key("f6",lambda _:self.Root.after(0,self.capturarTemplate,"botaospins"))
        keyboard.on_press_key("f5",lambda _:self.Root.after(0,self.capturarTemplate,"spins"))
        
        self.AtualizarBolas()
        self.atualizarTimer()
        self.monitorar()

    def caminhoDe(self,nome):
        return os.path.join("templates",f"template_{nome}.png")
    
    def carregarContador(self):
        if os.path.exists(self.arquivoSalvamento):
            try:
                with open(self.arquivoSalvamento,"r") as f:
                    dados = json.load(f)
                    return dados.get("prestiges",0),dados.get("spins",0),dados.get("ciclos",0),dados.get("tempo",0),dados.get("regioes",{})
            except (json.JSONDecodeError,ValueError):
                return 0,0,0,0,{}
        return 0,0,0,0,{}

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
            
    def ConfirmarSpins(self):
        if not self.AddSpins:
            if self.add not in ("","-"):
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
            "tempo":self.totalTempo,
            "regioes":self.regioes
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
            if self.spinBreak > self.MaxP:
                self.attCiclos(True)
                self.spinBreak = 1
            if self.spinBreak < 1:
                self.attCiclos(False)
                self.spinBreak = self.MaxP
            if qnt > 0 and self.spinBreak == self.MaxP:
                self.leituraPendente = True
                print("leitura armada")
        self.AtualizarBolas()

    def attCiclos(self,situacao):
        if situacao:
            self.ciclos+=1
            self.ciclosSessao+=1
        else:
            if self.ciclos > 0:
                self.ciclos-=1
                if self.ciclosSessao > 0:
                    self.ciclosSessao-=1
        self.label_ciclos.config(text=f"Cycles: {self.ciclosSessao}")
        self.label_statCycle.config(text=f"Session cycles: {self.ciclosSessao}")
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
        for i in range(self.MaxP):
            x1 = x + (i*espacamento) - raio
            x2 = x + (i*espacamento) + raio

            y1 = y - raio
            y2 = y + raio

            if i < self.spinBreak:
                cor = self.corSubt
            else:
                cor = ""
            if self.spinPres:
                if self.spinBreak == self.MaxP:
                    texto = "Go spin at 200"
                else: 
                    texto = f"Spinbreak in: {self.MaxP-self.spinBreak}"
            else:
                texto = "Disabled"
                cor = "red"
            self.canvas_bolas.create_oval(x1,y1,x2,y2,fill=cor,outline=self.corDestaque)

        self.label_spinbreak.config(text=f"{texto}")

    def atualizarTimer(self):
        if self.timerVisivel and self.AddSpins and not self.Pausado:
                self.label_tempo.config(fg=self.corSubt)
                self.label_statsTTime.config(fg=self.corTexto)
                self.label_statSTime.config(fg=self.corTexto)
                self.tempoSegundos+=1
                self.totalTempo+=1
        else:
            self.label_tempo.config(fg="red")
            self.label_statsTTime.config(fg="red")
            self.label_statSTime.config(fg="red")

        if self.PresCd > 0:
            self.PresCd-=1

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

    def iniciarArrastar(self,e):
        self.dx = e.x_root - self.Root.winfo_x()
        self.dy = e.y_root - self.Root.winfo_y()

    def arrastar(self,e):
        x = e.x_root - self.dx
        y = e.y_root - self.dy
        self.Root.geometry(f"+{x}+{y}")

    def monitorar(self):
        self.tick+=1
        self.prestigioVisivel = self.verificar("prestigio") >= self.acuracia
        if self.PresCd == 0 and self.prestigioVisivel:
            self.incrementar()
            self.PresCd = 30

        if self.tick  % 10 == 0:
            self.timerVisivel = self.verificar("timer") >= self.acuracia

        if self.leituraPendente and self.tick % 4 == 0:
            if self.verificar("botaospins") >= self.acuracia:
                self.framesMenu +=1
            else:
                self.framesMenu = 0

        if self.framesMenu >=2:
            self.leituraPendente = False
            self.framesMenu = 0
            self.Root.after(500,self.lerSpins)
        
        self.Root.after(50,self.monitorar)

    def capturarTemplate(self,nome):
        nomeJanela = "Selecione a area"
        with MSS() as sct:
            monitor = sct.monitors[1]
            sc = sct.grab(monitor)
            frame = np.array(sc)[:,:,:3]

        cv2.namedWindow(nomeJanela,cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(nomeJanela,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty(nomeJanela,cv2.WND_PROP_TOPMOST,1)    

        roi = cv2.selectROI(nomeJanela,frame,fromCenter=False,showCrosshair=True)
        x,y,w,h = roi
        frameGray = cv2.cvtColor(frame,cv2.COLOR_BGRA2GRAY)
        templateRecortado = frameGray[y:y+h, x:x+w]

        if w == 0 or h == 0:
            print("[AVISO] Seleção cancelada pelo usuário.")
            cv2.destroyWindow(nomeJanela)
            return False
        
        cv2.destroyWindow(nomeJanela)
        cv2.imwrite(self.caminhoDe(nome), templateRecortado)
        self.templates[nome] = templateRecortado
        self.regioes[nome] = {"left": int(x), "top": int(y), "width": int(w), "height": int(h)}
        self.salvar_contador()

    def salvarDebug(self):
        if self.ultimoFrame is not None:
            cv2.imwrite("debug.png", self.ultimoFrame)

    def verificar(self,nome):
        regiao = self.regioes.get(nome)
        template = self.templates.get(nome)
        if regiao is None or template is None:
            return 0

        m = 20
        area = {
            "left": max(0, regiao["left"] - m),
            "top": max(0, regiao["top"] - m),
            "width": regiao["width"] + m * 2,
            "height": regiao["height"] + m * 2
        }
        cinza = cv2.cvtColor(np.array(self.sct.grab(area)), cv2.COLOR_BGRA2GRAY)
        if cinza.shape[0] < template.shape[0] or cinza.shape[1] < template.shape[1]:
            return 0
        resultado = cv2.matchTemplate(cinza, template, cv2.TM_CCOEFF_NORMED)
        return cv2.minMaxLoc(resultado)[1]

    def lerSpins(self):
        regiao = self.regioes.get("spins")
        if regiao is None:
            return
        
        captura = self.sct.grab(regiao)
        img = np.array(captura)[:,:,:3]
        img = cv2.resize(img,None,fx=3,fy=3,interpolation=cv2.INTER_CUBIC)
        resultado = self.ocr(img)
        textos = resultado.txts
        if not textos:
            return
        texto = "".join(textos)
        digitos = "".join(c for c in texto if c.isdigit())
        if digitos == "":
            return
        valor = int(digitos)
        print(valor)
        min,max = 1,1200
        aceito = min <= valor <= max
        with open("leituras.log","a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} {texto!r} -> {valor} aceito={aceito}\n")
        if not aceito:
            print("Leitura rejeitada",valor)
            return
        self.spins += valor
        self.label_spins.config(text=str(self.spins))
        self.salvar_contador()

root = tk.Tk()
app = ContadorApp(root)
root.mainloop()