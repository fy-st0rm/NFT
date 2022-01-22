import pygame
import os
import itertools


# COLORS
ACTIVE = (255, 255, 255)
INACTIVE = (165, 165, 165)
BORDER = (165, 165, 165)

class Object:
	def __init__(self, surface, tag, image, x, y, object_list):
		self.surface = surface
		self.tag = tag
		self.image = image
		self.object_list = object_list

		self.x = x
		self.y = y
		self.w = self.image.get_width()
		self.h = self.image.get_height()
		self.prev = [0, 0]

		self.hold = False
		self.resize = False
	
	def event(self):
		if pygame.mouse.get_pressed()[0]:
			rect = pygame.Rect(self.x, self.y, self.w, self.h)
			pos = list(pygame.mouse.get_pos())
			pos[0] -= 100

			if rect.collidepoint(pos):
				for i in self.object_list:
					if i.hold and i != self:
						return
				
				self.x = pos[0] - self.w / 2
				self.y = pos[1] - self.h / 2
				self.hold = True
			else:
				self.hold = False
		
		elif pygame.mouse.get_pressed()[2]:
			rect = pygame.Rect(self.x, self.y, self.w, self.h)
			pos = list(pygame.mouse.get_pos())
			pos[0] -= 100
			
			if not self.resize:
				self.prev = pos
				self.resize = True
			else:
				if rect.collidepoint(pos):
					for i in self.object_list:
						if i.hold and i != self:
							return

					delta_x = pos[0] - self.prev[0]
					delta_y = pos[1] - self.prev[1]

					self.w += delta_x
					self.h += delta_y
					print(self.w, self.h)

					self.image = pygame.transform.scale(self.image, (self.w, self.h))
					
					self.hold = True
				else:
					self.hold = False
					self.resize = False

				self.prev = pos


	def draw_hitbox(self):
		pygame.draw.rect(self.surface, BORDER, [self.x, self.y, self.w, self.h], 2)
	
	def draw(self):
		self.surface.blit(self.image, (self.x, self.y))


class Engine:
	def __init__(self, surface, in_folder, out_folder, objects, layers):
		self.surface = surface
		self.in_folder = in_folder
		self.out_folder = out_folder
		self.objects = objects
		self.layers = layers

		self.data_struct = {} # Holds rect pos for the layer
		self.layer_struct = {} # Holds all the images according to the layers
		self.combinations = []

	def __gen_data_struct(self):
		for i in self.objects:
			self.data_struct[i.tag] = pygame.Rect(i.x, i.y, i.w, i.h)
		print(self.data_struct)

	def __load_images(self):
		for i in self.layers:
			new_path = self.in_folder + "/" + i
			images = os.listdir(new_path)
			
			self.layer_struct[i] = []
			for image in images:
				img_path = new_path + "/" + image
				img = pygame.image.load(img_path)
				self.layer_struct[i].append(img)

		print(self.layer_struct)

	def __gen_combinations(self):
		keys, values = zip(*self.layer_struct.items())
		self.combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
		print("Generated:", len(self.combinations))

	def run(self):
		self.__gen_data_struct()
		self.__load_images()
		self.__gen_combinations()
		
		os.system(f"rm {self.out_folder}/*")
		bg_dir = os.listdir(f"{self.in_folder}/BG")
		bg = []
		for i in bg_dir:
			image = pygame.image.load(f"{self.in_folder}/BG/{i}")
			image = pygame.transform.scale(image, (self.surface.get_width(), self.surface.get_height()))
			bg.append(image)

		print(bg)

		count = 0
		bg_index = 0
		for comb in self.combinations:
			print(f"Generated ({count}/{len(self.combinations)})")
			self.surface.fill((255, 255, 255))
			self.surface.blit(bg[bg_index], (0, 0))
			bg_index += 1
			if (bg_index >= len(bg)):
				bg_index = 0

			for layer in comb:
				rect = self.data_struct[layer]
				img = comb[layer]
				img = pygame.transform.scale(img, (rect.w, rect.h))
				self.surface.blit(img, (rect.x, rect.y))
			
			pygame.image.save(self.surface, f"{self.out_folder}/IMG_{count}.png")
			count += 1

		print(f"Generated {count} images at {self.out_folder}")
