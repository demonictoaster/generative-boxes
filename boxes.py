import cairo
import math
import numpy as np
import os
from tqdm import tqdm


"""
TODO: 
-
"""

params = {
	'canvas_width': 512,
	'canvas_height': 512,
	'bg_colors': np.array([249, 244, 239]) / 255,
	'n_boxes': 50,
	'size_first_box': 0.1,
	'avg_size': 0.0003,
	'std_size': 0.01,
	'p_filled': 0.05
}

root = os.path.abspath('')
out_folder = root + '/output'

class Box:

	def __init__(self, p1, p2, p3, p4):
		self.p1 = p1
		self.p2 = p2
		self.p3 = p3
		self.p4 = p4

		self.neighbors = {
			'top': False,  # True if neighbor box on top side
			'bot': False,
			'left': False,
			'right': False
		}
		
		# projections to axes (use longest side if not rectangle)
		# NOTE: doesn't work if box is rotated
		self.x = np.array([
			min(self.p1[0], self.p3[0]),
			max(self.p2[0], self.p4[0])
			])
		self.y = np.array([
			min(self.p1[1], self.p2[1]),
			max(self.p3[1], self.p4[1])
			])

		# is rectangle?
		self.rect = True

	def width(self):		
		w = self.p2[0] - self.p1[0]
		return w

	def height(self):
		h = self.p3[1] - p1[1]
		return h

	def get_coord(self):
		coord = np.array([self.p1, self.p2, self.p3, self.p4])
		return coord

	def center(self):
		center = np.array([(self.p1[0] + self.p2[0]) / 2, (self.p1[1] + self.p3[1]) / 2])
		return center

	def get_random_side(self):

		available = []

		for k in self.neighbors.keys():
			if self.neighbors[k] == False:
				available.append(k)

		if len(available) == 0:
			return 0

		else:
			choice = available[np.random.randint(0, len(available))]
			# self.neighbors[choice] = True
			return choice

def overlap(box1, box2):
	#NOTE: perfect overlap is fine, return False in this case
	if box1.x[1] > box2.x[0] and box2.x[1] > box1.x[0]:
		if box1.y[1] > box2.y[0] and box2.y[1] > box1.y[0]:
			return True
		else:
			return False
	else:
		return False


def get_corners(center, width, height):
	p1 = np.array([center[0] - width / 2, center[1] - height / 2])
	p2 = np.array([center[0] + width / 2, center[1] - height / 2])
	p3 = np.array([center[0] - width / 2, center[1] + height / 2])
	p4 = np.array([center[0] + width / 2, center[1] + height / 2])
	return p1, p2, p3, p4

def spawn_boxes(location, n, avg, std, pfill, prev_boxes):

	# first box
	p1, p2, p3, p4 = get_corners(location, avg, avg)
	boxes = [Box(p1, p2, p3, p4)]

	# spawn more boxes
	for i in tqdm(range(1, n)):

		while True:
			size = abs(np.random.normal(avg, std))
			prev_box = boxes[np.random.randint(len(boxes))]  # pick rdm box
			# prev_box = boxes[i-1]
			side = prev_box.get_random_side()
			print(side)

			if side == 'top':
				p3, p4 = prev_box.p1, prev_box.p2
				p1 = np.array([p3[0], p3[1] - size])
				p2 = np.array([p4[0], p4[1] - size])
				new_box = Box(p1, p2, p3, p4)
				new_box.neighbors['bot'] = True

			elif side == 'bot':
				p1, p2 = prev_box.p3, prev_box.p4
				p3 = np.array([p1[0], p1[1] + size])
				p4 = np.array([p2[0], p2[1] + size])
				new_box = Box(p1, p2, p3, p4)
				new_box.neighbors['top'] = True

			elif side == 'left':
				p2, p4 = prev_box.p1, prev_box.p3
				p1 = np.array([p2[0] - size, p2[1]])
				p3 = np.array([p4[0] - size, p4[1]])
				new_box = Box(p1, p2, p3, p4)
				new_box.neighbors['right'] = True

			elif side == 'right':
				p1, p3 = prev_box.p2, prev_box.p4
				p2 = np.array([p1[0] + size, p1[1]])
				p4 = np.array([p3[0] + size, p3[1]])
				new_box = Box(p1, p2, p3, p4)
				new_box.neighbors['left'] = True

			elif side == 0:
				pass

			# if overlap(prev_box, new_box) == False:
			# 	break
			breaches = []
			for b in (boxes + prev_boxes):
				breaches.append(overlap(b, new_box))
			if sum(breaches) == 0:
				break
			prev_box.neighbors[side] = True

		boxes.append(new_box)

		# adapt params as we progress
		if i % 50 == 0:
			avg /= 1.01
			std /= 1.01

	return boxes

def create_canvas(params):

	canvas_width = params['canvas_width']
	canvas_height = params['canvas_height']
	bg_colors = params['bg_colors']

	# initiate cairo context
	file = os.path.join(out_folder, 'boxes_.svg')
	img = cairo.SVGSurface(file, canvas_width, canvas_height)
	ctx = cairo.Context(img)
	ctx.set_line_width(0.001)

	# draw background
	ctx.set_source_rgb(bg_colors[0], bg_colors[1], bg_colors[2])
	ctx.rectangle(0, 0, canvas_width, canvas_height)
	ctx.fill()

	# scale space axes and other
	ctx.scale(canvas_width, canvas_height)    
	ctx.set_source_rgb(0,0,0)

	return ctx

def draw_box(ctx, box, p_fill = params['p_filled']):

	p1 = box.p1
	p2 = box.p2
	p3 = box.p3
	p4 = box.p4

	ctx.move_to(p1[0], p1[1])
	ctx.line_to(p2[0], p2[1])
	ctx.line_to(p4[0], p4[1])
	ctx.line_to(p3[0], p3[1])
	ctx.line_to(p1[0], p1[1])
	ctx.stroke()
	if np.random.rand() < p_fill:
		ctx.move_to(p1[0], p1[1])
		ctx.line_to(p2[0], p2[1])
		ctx.line_to(p4[0], p4[1])
		ctx.line_to(p3[0], p3[1])
		ctx.line_to(p1[0], p1[1])
		ctx.fill()

def main():
	boxes = []
	# for i in range(10):
	# 	loc = np.random.uniform(0.2, 0.8, size=2)
	# 	new_cluster = spawn_boxes(loc, np.random.uniform(50, 1000), 0.01, 0.01, 0.05, boxes)
	# 	boxes += new_cluster
	boxes += spawn_boxes(np.array([0.5, 0.5]), 2000, 0.01, 0.02, 0.05, boxes)
	# boxes += spawn_boxes(np.array([0.25, 0.25]), 1000, 0.0008, 0.01, 0.05, boxes)
	# boxes += spawn_boxes(np.array([0.75, 0.75]), 1000, 0.0008, 0.01, 0.05, boxes)

	ctx = create_canvas(params)
	ctx.set_line_join(cairo.LINE_JOIN_ROUND)

	# draw stuff
	for b in boxes:
		draw_box(ctx, b)



if __name__ == "__main__":
	main()
	pass
