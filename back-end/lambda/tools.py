from langchain.agents.tools import Tool
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    HumanMessage,
    SystemMessage
)
import requests
import os

yonaguni = """Vi que viste mi story y subiste una pa' mí
Yo que me iba a dormir, ey
En la disco habían mil
Y yo bailando contigo en mi mente

Aunque sé que no debo
Pensar en ti, bebé
Pero cuando bebo
Me viene tu nombre, tu cara
Tu risa y tu pelo, ey
Dime dónde tú está', que yo por ti cojo un vuelo
Y a Yonaguni le llego

Si me da' tu dirección, yo te mando mil carta'
Si me da' tu cuenta de banco, un millón de peso'
To'a la noche arrodillado a Dio' le rezo
Pa' que ante' que se acabe el año tú me de' un beso

Y empezar el 2023 bien cabrón
Contigo y un blunt
Tú te ve' asesina con ese mahón
Me matas sin un pistolón

Y yo te compro un Banshee
Gucci, Givenchy
Un poodle, un frenchie
El pasto, lo' munchie'
Te canto un mariachi
Me convierto en Itachi, eh

Yeah, yeah, yeah, yeah
Bad Bunny, baby, bebé
Bad Bunny, baby, bebé
"""

class Tools():
    def __init__(self) -> None:
        self.tools = [
            Tool(
                name="Make a Bad Bunny Rap",
                func=self.make_bad_bunny_rap,
                description="Use this tool to make a Bad Bunny rap about anything you want."
            ),
            Tool(
                name="Search Ticket Master",
                func=self.search_ticket_master,
                description="Use this tool to search for events on Ticket Master."
            )
        ]

    def make_bad_bunny_rap(self, input):
        # Pass Yonaguni lyrics to LLM as sample of Bad Bunny's style
        llm = ChatOpenAI(temperature=1, model_name="gpt-4")
        system_message="Here is a sample of Bad Bunny's style:\n" + yonaguni + "\n\nYour job is take the users input and write a rap in Bad Bunny's style. Make sure your rap is in the same language as the user's input. Keep it to three verses."
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=input)
        ]
        created_rap = llm(messages)
        return created_rap.content
    
    def search_ticket_master(self, input):
        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        params = {
            "apikey": os.environ["TICKET_MASTER_API_KEY"],
            "size": 5,
            "keyword": input
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        events = response.json()
        event_list = []
        if "_embedded" not in events:
            return "There are no events for that search."
        for event in events["_embedded"]["events"]:
            start_date = event["dates"]["start"]["localDate"]
            start_time = event["dates"]["start"]["localTime"]
            timezone = event["dates"]["timezone"]
            name = event["name"]
            price_range = str(event["priceRanges"][0]["min"]) + " to " + str(event["priceRanges"][0]["max"])
            # url = event["url"]
            event_sentence = "On " + start_date + " at " + start_time + " " + timezone + ", there is a " + name + " event. The price range is " + price_range + "."
            event_list.append(event_sentence)
        return event_list

tools = Tools().tools