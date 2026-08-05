from ai_agent import analyze_room


sensor = {

    "temperature":29.5,

    "humidity":78,

    "light":"OFF"

}


result = analyze_room(sensor)


print(result)