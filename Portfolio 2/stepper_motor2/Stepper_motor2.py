"""Run two synchronized stepper motors through drivers on GPIO pins 0-7."""

import math
#Importere matematiske funktioner, så jeg kan bruge sin og pi
import time
#Importere time så jeg kan bruge sleep funktionen til at lave en pause mellem hvert step

from machine import Pin
#Importere Pin fra machine, så jeg kan styre GPIO pins
from machine import PWM
#Importere PWM fra machine, så jeg kan styre PWM signaler på GPIO pins


class StepperMotor:
	#Opretter en klasse til steppermotoren som indenholder funktionerne og vairablerne for motoren
	PINS = (0, 1, 2, 3, 4, 5, 6, 7)
	#sætter min pins til GPIO pins 0-7
	PINS_PER_MOTOR = 4
	#sætter antal af pins per motor til at være 4
	STEP_DELAY = 0.005
	#sætter et delay mellem hvert step
	MICROSTEPS_PER_CYCLE = 64
	#sætter antallet af microsteps per cyklus til at være 64
	FULL_STEPS_PER_ROTATION = 200
	#Sætter antallet af fulde steps per rotation til at være 200 (Full steps)
	Val = 1
	SEQUENCES = {
		"full": (
			(Val, Val, 0, 0),
			(0, Val, Val, 0),
			(0, 0, Val, Val),
			(Val, 0, 0, Val),
			#Opretter en sequence for full step, hvor jeg fortæller hvilke coils der skal tændes og/eller slukkes
		),
		"half": (
			(Val, 0, 0, 0),
			(Val, Val, 0, 0),
			(0, Val, 0, 0),
			(0, Val, Val, 0),
			(0, 0, Val, 0),
			(0, 0, Val, Val),
			(0, 0, 0, Val),
			(Val, 0, 0, Val),
			#Gør det samme med half step, bare med flere mellemtrin imellem stepsene
		),
	}
	def __init__(self):
		#Opretter en contructor for steppermotoren, som initialiserer variablerne pins og outputs som tomme lister
		self.pins = []
		self.outputs = []

	def setup(self):
		for pin in self.PINS:
			#Tager pins fra listen pins
			output_pin = Pin(pin, Pin.OUT, value=0)
			#Sikre at deres starter værdi er sat til 0
			self.pins.append(output_pin)
			#Opbevare pins i en liste
			channel = PWM(output_pin)
			#Sætter PWM på pinsene
			self.outputs.append(channel)
			#opbevare PWM kanalerne i en liste
			channel.freq(16000)
			#Sætter frekvensen på PWM signalet til 16.000hz, så motoren ikke larmer
			channel.duty_u16(0)
			#sætter duty cycle til 0, så motoren ikke kører ved opstart

	def run_sequence(self, mode, steps, direction):
		#opretter en run_sequence funktion, som tager mode, steps og direction som argumenter
		sequence = self.SEQUENCES[mode]
		#Tager den sequence som er valgt i mode argumentet
		for step in range(steps):
			#tager et step for hvert step i steps argumentet
			pattern = sequence[(direction * step) % len(sequence)]
			#Definerer et pattern for hvert step, som er afhængig af direction og step nummeret
			for index, channel in enumerate(self.outputs):
				#Tager hvert index og channel i outputs listen
				on = pattern[index % self.PINS_PER_MOTOR]
				#Sætter on til at være 1 eller 0 afhængig af pattern og index
				channel.duty_u16(65535 if on else 0)
				#Sætter duty cycle til 65535 hvis on er 1, ellers sætter den duty cycle til 0
			time.sleep(self.STEP_DELAY)
			#sætter en pause mellem hvert step, så motoren ikke kører for hurtigt

	def micro_step(self, step, direction):
		#opretter en adskilt funktion for microstepping, som tager step og direction som argumenter
		angle = direction * 2 * math.pi * (step % self.MICROSTEPS_PER_CYCLE) / self.MICROSTEPS_PER_CYCLE
		#Beregner vinklen for hvert microstep, som er afhængig af direction og step nummeret
		for index, channel in enumerate(self.outputs):
			#Tager hvert index og channel i outputs listen
			phase = index % self.PINS_PER_MOTOR
			#Beregner phase for hvert channel, som er afhængig af index
			level = max(0.0, math.sin(angle - phase * math.pi / 2))
			#Beregner level for hvert channel, som er afhængig af angle og phase
			channel.duty_u16(round(level * 65535))
			#Sætter duty cycle for hvert channel, som er afhængig af level
		time.sleep(self.STEP_DELAY / 4)
		#Sætter en pause mellem hvert microstep, som er kortere end for full og half step, så motoren kører mere smooth

	def steps_for_rotations(self, mode, rotations):
		#laver en funktion som beregner hvor mange steps der skal til for et antal rotationer, afhængig af mode
		if mode == "half":
			step_factor = 2
			#hvis det er half, skal mængden af steps ganges med 2, da der er dobbelt så mange steps i half step
		elif mode == "micro":
			step_factor = self.MICROSTEPS_PER_CYCLE // len(self.SEQUENCES["full"])
			#hvis det er micro, skal mængden af steps ganges med antallet af microsteps per cycle divideret med antallet af fulde steps i en rotation
		else:
			step_factor = 1
		return round(rotations * self.FULL_STEPS_PER_ROTATION * step_factor)
		#Beregner hvor mange steps der skal til for et antal rotationer, afhængig af mode

	def shutdown(self):
		#laver en shutdown funktion, som sikre at alt er sat til 0 og deinit, så motoren ikke kører videre efter programmet er stoppet
		for channel in self.outputs:
			channel.duty_u16(0)
			channel.deinit()
		for output_pin in self.pins:
			output_pin.init(Pin.OUT, value=0)
		self.outputs = []
		self.pins = []

	def run(self):
		#laver en run funktion, som kører programmet og spørger brugeren om input
		while True:
			#starter mit while true loop, som kører indtil brugeren vælger at stoppe programmet
			try:
				mode = input("Choose sequence (full, half, micro; q to quit): ").strip().lower()
				#spørger brugeren om hvilken sequence der skal køres, og fjerner mellemrum, samt sætter input til lower case
				if mode in ("q", "quit"):
					break
				#sikre at programmet stopper hvis brugeren vælger q eller quit
				if mode not in ("full", "half", "micro"):
					print("Please choose full, half, micro, or q to quit.")
					#hvis brugeren ikke vælger en af de tre sequences, bliver der printet en besked om at vælge en af de tre sequences
					continue
				direction_choice = input("Direction (forward/backward): ").strip().lower()
				#Spørger brugeren om det skal gå fremad eller bagud
				if direction_choice in ("forward", "f"):
					direction = 1
					#Hvis fremad vælges, sættes direction til 1
				elif direction_choice in ("backward", "reverse", "b", "r"):
					direction = -1
					#Hvis bagud vælges, sættes direction til -1
				else:
					print("Please choose forward or backward.")
					#hvis intet er valgt, bliver de bedt om at vælge igen
					continue

				unit = input("Move by steps or rotations? ").strip().lower()
				#Bliver spurgt om de vil køre i steps eller rotations
				if unit in ("step", "steps", "s"):
					try:
						steps = int(input("How many steps? ").strip())
						#hvis de har valgt steps, bliver de spurgt om hvor mange steps de vil køre
					except ValueError:
						print("Please enter a positive whole number of steps.")
						#hvis det ikke er et heltal, bliver de bedt om at vælge igen
						continue
				elif unit in ("rotation", "rotations", "r"):
					try:
						rotations = float(input("How many 360-degree rotations? ").strip())
						#Hvis de har valgt rotations, bliver de spurgt om hvor mange rotationer de vil køre
					except ValueError:
						print("Please enter a real number of rotations.")
						#hvis det ikke er et tal, bliver de bedt om at vælge igen
						continue
					if rotations <= 0:
						print("Please enter a positive number of rotations.")
						#hvis tallet er mindre end eller lig med 0, bliver de bedt om at vælge igen
						continue
					steps = self.steps_for_rotations(mode, rotations)
					#tallerne bliver konverteret til steps, ved at kalde steps_for_rotations funktionen, ud fra step_factor og rotations
				else:
					print("Please choose steps or rotations.")
					#hvis de ikke vælger steps eller rotations, bliver de bedt om at vælge igen
					continue

				if steps <= 0:
					print("That amount is smaller than one step in this mode.")
					#hvis steps er mindre end eller lig med 0, bliver de bedt om at vælge igen
					continue

				print("Running {} steps {}. Press Ctrl-C to stop early.".format(steps, direction_choice))
				#Printer hvor mange steps der skal køres, og i hvilken retning
				try:
					self.setup()
					#Sætter pins og PWM kanaler op
					if mode == "micro":
						for step in range(steps):
							self.micro_step(step, direction)
							#hvis micro mode er valgt, bliver micro_step funktionen kaldt for hvert step
					else:
						self.run_sequence(mode, steps, direction)
						#hvis full eller half mode er valgt, bliver run_sequence funktionen kaldt for hvert step
				except KeyboardInterrupt:
					print("Stopping: setting the sequence and outputs to 0.")
					#hvis brugeren trykker Ctrl-C, bliver der printet en besked om at stoppe, og at outputs bliver sat til 0
				finally:
					self.shutdown()
					#sikre at alt er blevet sat til 0 og deinit, så motoren ikke kører videre efter programmet er stoppet
				print("Outputs off. Choose another mode or enter q to quit.")
				#printer en besked om at outputs er slukket
			except KeyboardInterrupt:
				print("Exiting.")
				self.shutdown()
				break
			    #hvis brugeren trykker Ctrl-C, bliver der printet en besked om at programmet afsluttes, og at outputs bliver sat til 0
