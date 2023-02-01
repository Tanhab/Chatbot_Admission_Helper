from Chatbot import GenericAssistant



assistant = GenericAssistant(
    load=True)
#assistant.train_model()
#assistant.save_model()
#assistant.load_model(model_name="test_model")

done = False

while not done:
    message = input("Enter a message: ")
    if message == "STOP":
        done = True
    else:
        reply = assistant.request(message)
        print("reply", reply)
