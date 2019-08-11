import cairo
import math
import numpy as np
import os


"""
TODO: 
-
"""

params = {
	'canvas_width': 512,
	'canvas_height': 512,
	'bg_colors': np.array([249, 244, 239]) / 255,
	'n_boxes': 20,
	'size_first_box': 0.1,
	'avg_size': 0.01,
	'std_size': 0.03,
	'p_filled': 0.03
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

# first box
size = params['size_first_box']
p1, p2, p3, p4 = get_corners(np.array([.5, .5]), size, size)
boxes = [Box(p1, p2, p3, p4)]

# spawn more boxes
for b in range(1, params['n_boxes']):

	while True:
		size = abs(np.random.normal(params['avg_size'], params['std_size']))
		prev_box = boxes[np.random.randint(len(boxes))]  # pick rdm box
		side = prev_box.get_random_side()

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

		if overlap(prev_box, new_box) == False:
			break

		prev_box.neighbors[side] = True
		print(side)
		print(new_box.get_coord())

	boxes.append(new_box)


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

def draw_rectangle(ctx, box, p_fill = params['p_filled']):

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

	ctx = create_canvas(params)
	ctx.set_line_join(cairo.LINE_JOIN_ROUND)

	# draw stuff
	for b in boxes:
		draw_rectangle(ctx, b)



if __name__ == "__main__":
	main()
	pass
