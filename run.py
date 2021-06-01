import pyglet 
import math 
import os
import neat
import sys

from pyglet.window import Window
from pyglet.window import key

from physobj import PhysicalObject
from road import Road
from agent import Player       

win = pyglet.window.Window(1300, 1000)
game_batch = pyglet.graphics.Batch()

game_road = Road(x=0,y=0,batch=game_batch)

# Define score 
score_label = pyglet.text.Label(text="Score: 0", x=190, y=500, font_size=30)
generation_label = pyglet.text.Label(text="Generation: 0", x=190, y=540, font_size=30)
max_fitness_label = pyglet.text.Label(text="Max Fitness: 0", x=190, y=580, font_size=30)
avg_fitness = pyglet.text.Label(text="Avg Fitness: 0", x=190, y=620, font_size=30)
alive_label = pyglet.text.Label(text="Alive cars: 0", x=190, y=620, font_size=30)

score = 1
cars = []

def fitness(pop):
	global score
	for genome, car in zip(pop, cars):
		genome['fitness'] = car.genome['fitness']

save = None

if len(sys.argv) > 1:
	save = True

nn = neat.main(fitness, gen_size=99999, pop_size=15, save=save)
pop = []
generation = 0
max_fitness = 1
avg_fitness = 1
alive_cars = 0        

def restart():
	global fittest, fittest_act, max_fitness, pop, avg_fitness, score
	global generation, max_fitness
	generation += 1
	pop = next(nn)
	max_fitness = max(max_fitness, score)
	avg_fitness = sum(x['fitness'] for x in pop)/len(pop)

	# Set score to 0
	score = 0
	score_label.text = "Рекорд: {}".format(score)
	generation_label.text = "Поколение: {}".format(generation)
	max_fitness_label.text = "Макс. добротность: {}".format(max_fitness)

	global cars

	for car in cars:
		car.delete()

	cars = []
	for genome in pop:
		car = Player(x=380,y=870,batch=game_batch)
		car.genome = genome
		car.activate = neat.generate_network(genome)
		cars.append(car)	

@win.event
def on_draw():
	win.clear()
	game_batch.draw()
	score_label.draw()
	generation_label.draw()
	max_fitness_label.draw()
	alive_label.draw()

def update(dt):
	global score

	alive_label.text = "Живые агенты: {}".format(len([x for x in cars if x.alive]))

	dt = dt / 1.8

	for car in cars:
		if car.alive:
			if len(car.radars) != 0:
				r = car.radars
				p1, d1 = r[0] # Sry for busy code
				p2, d2 = r[1]
				p3, d3 = r[2]
				p4, d4 = r[3]
				p5, d5 = r[4]
				nn_in = (d1,d2,d3,d4,d5,car.forward_velocity())
				if car.forward_velocity() < 200:
					 	car.forward(dt)	
				#print(" : "car.activate(nn_in)[0])
				if car.activate(nn_in)[0] > 0.5:
					if d1 < 49 or d2 < 59:
						car.right(dt)
					if d4 < 49 or d5 < 59:
						car.left(dt)
					if d3 > 30:
						car.forward(dt)
					else:
						car.backward(dt)					
		car.update(dt, game_batch, game_road)
		#car.draw_radars(game_batch)
		#car.draw_collision_points(game_road, game_batch)
							
	for car in cars:
		if car.alive == False:
			car.genome['fitness'] = score		

	if len([g for g in cars if g.alive]) == 0:
		# if no gamers are alive, start next generation
		pyglet.clock.unschedule(update)
		print("Dead. Restarting..")
		init()
		return

	score += 10 * dt
	score_label.text = "Рекорд: {}".format(int(score))	

def init():
	restart()
	pyglet.clock.schedule_interval(update, 1 / 120.0)

if __name__ == '__main__':
	init()
	pyglet.app.run()