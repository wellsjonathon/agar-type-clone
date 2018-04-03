# Add your World, Cell and Game code here
dotKV = '''\
<Game>:
  # Instantiate ObjectProperties
  # world: world
  # player: player
  # Add components to Game
  # World:
  #   id: world
  # Player:
  #   id: player

<World>:
  canvas:
    Color:
      rgba: [0,0,0.1,1]
    Rectangle:
      pos: [root.x, root.y]
      size: [root.width, root.height]

<Player>:
  x: 100
  y: 100
  r: 10
  color: [1,0,0,1]
  canvas:
    Color:
      rgba: self.color
    Ellipse:
      pos: self.x - self.r, self.y - self.r
      size: self.r*2, self.r*2

<Enemy>:
  canvas:
    Color:
      rgba: self.color
    Ellipse:
      pos: self.x - self.r, self.y - self.r
      size: self.r*2, self.r*2

<WinMessage>:
  size: self.texture_size
  font_size: '50sp'
  text: self.player + " wins!"
\
'''
from kivy.lang import Builder
Builder.load_string(dotKV)

from kivy.config import Config
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'width', '850')
Config.set('graphics', 'height', '480')

from kivy.core.window import Window
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.properties import ListProperty, NumericProperty, ObjectProperty, BooleanProperty, StringProperty
from kivy.clock import Clock

import random as r
import math as math
from itertools import combinations

class InputHandler (Widget):

  left = BooleanProperty(False)
  right = BooleanProperty(False)
  down = BooleanProperty(False)
  up = BooleanProperty(False)

  def __init__(self, **kwargs):
    self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
    self._keyboard.bind(on_key_down = self._on_keyboard_down)
    self._keyboard.bind(on_key_up = self._on_keyboard_up)

  def _keyboard_closed(self):
    self._keyboard.unbind(on_key_down = self._on_keyboard_down)
    self._keyboard.unbind(on_key_up = self._on_keyboard_up)
    self._keyboard = None

  def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'up':
      self.up = True
    if keycode[1] == 'down':
      self.down = True
    if keycode[1] == 'left':
      self.left = True
    if keycode[1] == 'right':
      self.right = True

  def _on_keyboard_up(self, keyboard, keycode):
    if keycode[1] == 'up':
      self.up = False
    if keycode[1] == 'down':
      self.down = False
    if keycode[1] == 'left':
      self.left = False
    if keycode[1] == 'right':
      self.right = False

class WinMessage (Label):
  
  player = StringProperty("")

class Game (FloatLayout):

  world = ObjectProperty(None)
  player = ObjectProperty(None)
  enemies = []
  num_enemies = 10
  inputHandler = ObjectProperty(InputHandler())

  def __init__(self, **kwargs):
    FloatLayout.__init__(self, **kwargs)
    self.world = World()
    self.player = Player(x = 100, y = 100, r = 50, color = [1,0,0,1])
    self.add_widget(self.world)
    self.add_widget(self.player)
    for i in range(self.num_enemies):
      self.enemies.append(
        Enemy(x = r.randint(40, 810), y = r.randint(40, 440),
              v_x = r.uniform(-0.5, 0.5), v_y = r.uniform(-0.5, 0.5),
              r = r.randint(5, 40), color = [r.uniform(0, 1.0), r.uniform(0, 1.0), r.uniform(0, 1.0), 1]))
      self.add_widget(self.enemies[i])
    Clock.schedule_interval(self.update, 1.0/60.0)
    # Add an enemy here

  def update (self, *args):
    # Check win conditions
    if (not self.enemies):
      winMessage = WinMessage(player = "Player 1")
      self.add_widget(winMessage)
      return False

    # Player move function
    self.player.move(self.inputHandler)
    # Collision detection for player and all enemies and enemy move function
    for i in range(len(self.enemies)):
      self.player.collisionResolution(self.player, self.enemies[i])
      self.enemies[i].move()
      # for j in range(len(self.num_enemies)):
      #   if (i != j):
      #     self.enemies[i].collisionResolution(self.enemies[i], self.enemies[j])
    for pair in list(combinations(self.enemies, 2)):
      pair[0].collisionResolution(pair[0], pair[1])
      # Note: use timeit to determine if doing this as a separate loop with
      # combinations is faster than doing this in the previous loop
      # My theory is doing the nested for loop is faster since I have to
      # do the initial loop regardless
    # Clean up consumed cells
    self.clean()

  def clean (self, *args):
    for enemy in self.enemies:
      if (enemy.r <= 0):
        self.remove_widget(enemy)
        self.enemies.remove(enemy)


class World (Widget):
  def __init__(self, **kwargs):
    Widget.__init__(self, **kwargs)

class Cell (Widget):

  color = ListProperty([])
  x = NumericProperty(0)
  y = NumericProperty(0)
  v_x = NumericProperty(0)
  v_y = NumericProperty(0)
  r = NumericProperty(0)
  V_MAX = NumericProperty(2.5)

  def __init__(self, **kwargs):
    Widget.__init__(self, **kwargs)

  def move(self):
    # Clamp v_x to V_MAX
    if (self.v_x > self.V_MAX):
      self.v_x = self.V_MAX
    elif (self.v_x < -self.V_MAX):
      self.v_x = -self.V_MAX
    # Clamp v_y to V_MAX
    if (self.v_y > self.V_MAX):
      self.v_y = self.V_MAX
    elif(self.v_y < -self.V_MAX):
      self.v_y = -self.V_MAX

    # Update position
    self.x += self.v_x
    self.y += self.v_y

    # Ensure position remains in bounds
    # Right
    if (self.x + self.r > Window.width):
      self.x = Window.width - self.r
      self.v_x = -self.v_x
    # Left
    if (self.x - self.r < 0):
      self.x = 0 + self.r
      self.v_x = -self.v_x
    # Top
    if (self.y + self.r > Window.height):
      self.y = Window.height - self.r
      self.v_y = -self.v_y
    # Bottom
    if (self.y - self.r < 0):
      self.y = 0 + self.r
      self.v_y = -self.v_y

  def collisionResolution(self, cell_1, cell_2):
    # Check to see if the two cells are colliding
    if (((cell_2.x - cell_1.x) ** 2) + ((cell_2.y - cell_1.y) ** 2) < ((cell_2.r + cell_1.r) ** 2)):
      # Figure out which cell is bigger/smaller
      bigger = cell_1 if cell_1.r > cell_2.r else cell_2
      smaller = cell_1 if cell_1.r < cell_2.r else cell_2

      # Return if the smaller cell is consumed
      if (smaller.r < 0):
        return

      # Compute the sum of the two cells' areas
      smaller_area = smaller.r ** 2
      bigger_area = bigger.r ** 2
      area_sum = smaller_area + bigger_area
      # Compute the gain factor (sum of areas divided by smaller area)
      gain = area_sum / smaller_area
      # Compute the area ratio (sqrt of bigger area/smaller area)
      area_ratio = math.sqrt(bigger_area / smaller_area)
      # Consumption factor (smaller value = faster consumption)
      consumption_factor = 120
      # Decrease smaller cell's radius by (gain factor * area ratio / consumption factor)
      smaller.r -= (gain * area_ratio / consumption_factor)
      # Return if the smaller cell is consumed (negative radius)
      if (smaller.r < 0):
        return
      # Set bigger radius to (sqrt of sum of areas - smaller area)
      smaller_area = smaller.r ** 2
      bigger.r = math.sqrt(area_sum - smaller_area)

    #   # Swap x and y velocities
    #   cell_1.v_x, cell_2.v_x = cell_2.v_x, cell_1.v_x
    #   cell_1.v_y, cell_2.v_y = cell_2.v_y, cell_1.v_y


class Player (Cell):
  def __init__(self, **kwargs):
    Cell.__init__(self, **kwargs)

  def move(self, inputHandler):
    # Apply input
    if (inputHandler.left):
      self.v_x -= 0.1
    if (inputHandler.right):
      self.v_x += 0.1
    if (inputHandler.up):
      self.v_y += 0.1
    if (inputHandler.down):
      self.v_y -= 0.1

    # Apply movement rules
    super(Player, self).move()


class Enemy (Cell):
  def __init__(self, **kwargs):
    Cell.__init__(self, **kwargs)

class GameApp(App):
  def build(self):
    return Game()

if __name__ == "__main__":
  GameApp().run()