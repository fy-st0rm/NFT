import sys
from engine import *
import threading

#TODO: [ ] Resizable objects
#TODO: [X] Generate images

class Layer:
	def __init__(self, surface, width, height):
		self.surface = surface
		self.width = width
		self.height = height
		self.texture = pygame.Surface((width, height))

		self.img_size = 70
		self.order = {}
		self.selected = None

	def init_layers(self):
		for i in self.order:
			self.order[i] = pygame.transform.scale(self.order[i], (self.img_size, self.img_size))

	def get_layers_order(self):
		return self.order.keys()

	def event(self, event):
		if event.type == pygame.KEYDOWN:
			# Brings a selected image up a layer
			if event.key == pygame.K_UP:
				if self.selected:
					index = 0
					for i in self.order:
						if i == self.selected:
							break
						index += 1

					tups = list(self.order.items())
					tups[index - 1], tups[index] = tups[index], tups[index - 1]
					self.order = dict(tups)

			# Brings a selected image down a layer
			if event.key == pygame.K_DOWN:
				if self.selected:
					index = 0
					for i in self.order:
						if i == self.selected:
							break
						index += 1

					tups = list(self.order.items())
					if index < len(self.order) - 1:
						tups[index + 1], tups[index] = tups[index], tups[index + 1]
					self.order = dict(tups)

		if pygame.mouse.get_pressed()[0]:
			temp = self.order.copy()
			x = y = 20 
			for i in temp:
				rect = pygame.Rect(x, y, self.img_size, self.img_size)
				pos = pygame.mouse.get_pos()

				if rect.collidepoint(pos):
					self.selected = i

				y += self.order[i].get_height() + 5


	def draw(self):
		self.surface.blit(self.texture, (0, 0))
		self.texture.fill((0, 0, 0))
		pygame.draw.rect(self.surface, BORDER, [0, 0, self.width, self.height], 1)

		x = y = 20
		for i in self.order:
			self.texture.blit(self.order[i], (x, y))

			if i == self.selected:
				pygame.draw.rect(self.surface, ACTIVE, [x, y, self.img_size, self.img_size], 1)
			else:
				pygame.draw.rect(self.surface, INACTIVE, [x, y, self.img_size, self.img_size], 1)
			y += self.order[i].get_height() + 5

class UI:
	def __init__(self, width, height):
		self.screen = pygame.display.set_mode((width, height))
		self.width, self.height = self.screen.get_width(), self.screen.get_height()
		self.surface = pygame.Surface((self.width - 100, height))
		self.objects = []

		self.layer_tab = Layer(self.screen, 100, self.height)

		# Flags
		self.loop	 = True
		self.hitbox  = False
		self.ctrl	 = False
		self.eng_run = False

	def __load_images(self):
		# This function loads individual parts of each sub dirs
		path = sys.argv[1]
		sub_dir = os.listdir(path)
		for i in sub_dir:
			if i != "BG":
				new_path = path + "/" + i
				images = os.listdir(new_path)
				image_path = new_path + "/" + images[0]
				image = pygame.image.load(image_path)

				# Adding the image in the layer list
				self.layer_tab.order[i] = image

				# Resizing the images
				width = image.get_width()
				height = image.get_height()
				ratio = width / height

				new_height = 600
				new_width = int(new_height * ratio)

				image = pygame.transform.scale(image, (new_width, new_height))
				new_obj = Object(self.surface, i, image, 0, 0, []) 
				self.objects.append(new_obj)

	def __give_pos(self):
		x = y = 0
		for i in self.objects:
			i.object_list = self.objects
			i.y = y
			x += i.w + 5
	
	def __start_engine(self):
		self.eng_run = True
		engine = Engine(self.surface, sys.argv[1], sys.argv[2], self.objects, self.order)
		engine.run()

	def __event(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.loop = False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_h:
					if self.hitbox:
						self.hitbox = False
					else:
						self.hitbox = True

				elif event.key == pygame.K_LCTRL:
					self.ctrl = True

				elif event.key == pygame.K_g:
					if self.ctrl and not self.eng_run:
						self.__start_engine()

			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LCTRL:
					self.ctrl = False

			self.layer_tab.event(event)

	def __render(self):
		self.order = self.layer_tab.get_layers_order()
		temp = self.objects.copy()
		self.objects.clear()

		# Sorting according to the layers
		for i in self.order:
			for j in temp:
				if i == j.tag:
					self.objects.append(j)

		# Rendering the images
		for i in self.objects:
			i.event()
			i.draw()
			if self.hitbox:
				i.draw_hitbox()

		self.layer_tab.draw()

	def run(self):
		self.__load_images()
		self.__give_pos()
		self.layer_tab.init_layers()

		clock = pygame.time.Clock()

		while self.loop:
			clock.tick(60)
			self.surface.fill((0, 0, 0))
			self.__event()
			self.__render()

			self.screen.blit(self.surface, (100, 0))
			pygame.display.update()

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("USAGE: nft [input_folder] [output_folder]")
		quit()

	pygame.init()
	app = UI(800, 600)
	app.run()

