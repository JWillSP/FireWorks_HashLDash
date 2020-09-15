
import math
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.widget import Widget
from random import random, randrange
from kivy.graphics import Color, Ellipse
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ListProperty, BooleanProperty


KV = '''
BoxLayout:
    Ceu:
        width: root.width
<Ceu>

'''

PI = math.pi
FPS = 60  # FPS
DT = 1/FPS  # INTERVALO DE TEMPO
G = -800
FOGUETE_SIZE = [10, 10]
SUB_PARTICULA_SIZE = [10, 10]
FIRE_NUMBER = 14
SPEED_EXPLOSION = 500


class Sub_particula(Widget):
    mytime = NumericProperty()
    active = BooleanProperty(False)
    velx = NumericProperty()
    cross_pos = ListProperty([0, 0])
    mass = NumericProperty()

    def __init__(
        self,
        angulo,
        velxi=0,
        size=SUB_PARTICULA_SIZE,
        color=[1, 1, 1, 1], **kwargs
    ):
        super().__init__(**kwargs)
        self.mass = 1
        self.size = size
        self.size_hint = None, None
        self.g = G
        self.active = False
        self.angulo = angulo
        self.vel = [
            velxi + SPEED_EXPLOSION*math.cos(angulo),
            SPEED_EXPLOSION*math.sin(angulo)
        ]
        self.color = Color(color.r, color.g, color.b, 0)
        self.ellipse = Ellipse(pos=[-20, -20], size=SUB_PARTICULA_SIZE)
        self.canvas.add(self.color)
        self.canvas.add(self.ellipse)

    def on_cross_pos(self, instance, pos):
        """
        Esta função é disparada toda vez que a Kivy_Property cross_pos sofrer
        mudança. No caso isso ocorre quando é atribuida a posição da explosão
        """
        self.vel[0] = self.velx + SPEED_EXPLOSION*math.cos(self.angulo)
        self.vel[1] = SPEED_EXPLOSION*math.sin(self.angulo)
        self.pos = pos
        self.mass = 1

    def on_mytime(self, instance, tempo):
        """
        Esta função é disparada toda vez que a kivy_Property mytime sofrer
        mudança. No caso isso ocorre quando o 'tempo' cresce na frequencia do
        FPS. Essa função dispara as atualições de velocidade e posição chamando
        a função update.
        """
        if self.active and self.mass > 0.5:
            self.update()
        else:
            self.mass = 0
            self.color.a = 0

    def update(self):
        self.vel[1] += self.g*DT
        self.vel[0] *= math.sqrt(self.mass)
        self.vel[1] *= math.sqrt(self.mass)
        self.y += self.vel[1]*DT
        self.x += self.vel[0]*DT
        self.ellipse.pos = self.pos
        self.color.a = self.mass**(4)
        self.mass *= 0.993


class Particula(Widget):
    mytime = NumericProperty()
    active = BooleanProperty()
    not_active = BooleanProperty()
    velx = NumericProperty()
    cross_pos = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = None, None
        self.g = G
        self.active = False
        self.not_active = not self.active
        self.size = FOGUETE_SIZE
        self.velx = randrange(-280, 280)
        self.vely = randrange(1000, 1300)
        self.angulos = [i*2*PI/FIRE_NUMBER for i in range(FIRE_NUMBER)]
        self.color = Color(
            math.sqrt(random()),
            math.sqrt(random()),
            math.sqrt(random()),
            1
        )
        self.ellipse = Ellipse(pos=self.pos, size=self.size)
        self.canvas.add(self.color)
        self.canvas.add(self.ellipse)
        for angulo in self.angulos:
            sub = Sub_particula(angulo=angulo, color=self.color)
            self.bind(mytime=sub.setter("mytime"))
            self.bind(velx=sub.setter("velx"))
            self.bind(cross_pos=sub.setter("cross_pos"))
            self.bind(not_active=sub.setter("active"))
            self.add_widget(sub)

    def set_initials(self):
        """
        Esta fução reseta os valores toda vez que há uma explosão
        """
        self.pos = [
            randrange(
                int(self.parent.width*3/8),
                int(self.parent.width*5/8)
            ),
            0
        ]
        self.size = FOGUETE_SIZE
        self.vel = [randrange(-280, 280), randrange(1000, 1300)]
        self.velx = self.vel[0]

    def on_mytime(self, instance, tempo):
        if self.active:
            self.update()
            if self.vel[1] <= 0:
                self.cross_pos = self.pos
                self.active = False
                self.not_active = not self.active
                self.set_initials()
                self.color.a = 0
        else:
            if random() >= 0.993:
                self.active = True
                self.not_active = not self.active
                self.color.a = 1

    def update(self):
        self.vel[1] += self.g*DT
        self.y += self.vel[1]*DT
        self.x += self.vel[0]*DT
        self.ellipse.pos = self.pos


class Ceu(FloatLayout):
    mytime = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.wait, 3)

    def wait(self, *args):
        for i in range(15):
            self.add_particula()
        self.mytime = 0
        Clock.schedule_interval(self.update, DT)

    def add_particula(self):
        p = Particula(
            pos=[
                randrange(
                    int(self.parent.width*3/8),
                    int(self.parent.width*5/8)
                ),
                0
            ]
        )
        self.bind(mytime=p.setter("mytime"))
        self.add_widget(p)
        p.set_initials()

    def update(self, *args):
        self.mytime += DT


class MainApp(MDApp):

    def build(self):
        self.theme_cls.theme_style = "Dark"
        return Builder.load_string(KV)

    def on_start(self):
        self.fps_monitor_start()


MainApp().run()
