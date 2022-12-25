from Chatbot import GenericAssistant


def function_for_greetings():
    print("You triggered the greetings intent!")
    # Some action you want to take


def function_for_stocks():
    print("You triggered the stocks intent!")
    # Some action you want to take


mappings = {'greeting': function_for_greetings, 'stocks': function_for_stocks}

assistant = GenericAssistant('intents.json', intent_methods=mappings, model_name="test_model")
assistant.train_model()
assistant.save_model()

done = False

while not done:
    message = input("Enter a message: ")
    if message == "STOP":
        done = True
    else:
        assistant.request(message)
