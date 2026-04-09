#fråga användaren efetr namn på roboten
namn_input = input("Vad ska robotgräsklipparen heta? ")
#om användaren inte skriver något, sätt namnet till "Per" annars, sätt namnet till det användaren skrev in.
if namn_input == "":
    robot_namn = "Per"
else:
    robot_namn = namn_input

print("Robotgräsklipparen heter " + robot_namn + "!")