import speech_recognition as sr

def speech():
    reconocedor = sr.Recognizer()

    with sr.Microphone() as mic:
        print("Ajustando ruido ambiente...")
        reconocedor.adjust_for_ambient_noise(mic, duration=1)
        print("Habla ahora...")
        audio_data = reconocedor.listen(mic)
        print("Reconociendo...")
        texto = reconocedor.recognize_google(audio_data, language="es-ES")
        texto = texto.lower()
        return texto 