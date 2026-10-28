from Stepper_motor2 import StepperMotor
#Importere StepperMotor klassen fra Stepper_Stepper_motor2.py filen, så jeg kan styre den fra denne fil


def main():
	motor = StepperMotor()
	motor.run()
	#Opretter en instans af StepperMotor klassen, og kalder run() metoden for at starte motoren

if __name__ == "__main__":
	main()
	#Hvis denne fil køres som hovedprogram, kaldes main() funktionen