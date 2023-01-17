import mesa
import mesa_geo as mg

from model import GeoSir
from agents import PersonAgent, ElephantAgent


"""class Steps_display(mesa.visualization.TextElement):

    def __init__(self):
        pass

    def render(self, model):
        return "Steps: " + str(model.steps)"""

class Dead_people_display(mesa.visualization.TextElement):

    def __init__(self):
        pass

    def render(self, model):
        return "Dead people: " + str(model.counts["affected"]) 
class Dead_elephant_display(mesa.visualization.TextElement):

    def __init__(self):
        pass

    def render(self, model):
        return "Dead Elephants: " + str(model.counts["dead"])                        


model_params = {
    "elephant_pop_size": mesa.visualization.Slider("Elephant Population size", 30, 20, 100, 5),
    "human_pop_size": mesa.visualization.Slider("Human Population size", 60, 50, 500, 10),
    "exposure_distance": mesa.visualization.Slider("Exposure distance", 12, 10, 30, 2),
    "number_of_steps": mesa.visualization.Slider("number of steps", 700, 500, 2000, 100),
}

def infected_draw(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = dict()

    if isinstance(agent, PersonAgent):
        portrayal["radius"] = "2"
    if isinstance(agent, ElephantAgent):
        portrayal["radius"] = "4"

    if agent.atype in ["hotspot", "affected"]:
        portrayal["color"] = "White"
    elif agent.atype in ["safe", "not_affected"]:
        portrayal["color"] = "Green"    
    elif agent.atype in ["harm"]:
        portrayal["color"] = "Red"
    elif agent.atype in ["not_harm"]:
        portrayal["color"] = "Black"
    elif agent.atype in ["dead"]:
        portrayal["color"] = "White"
    return portrayal


#steps_text = Steps_display()
dead_people_text = Dead_people_display()
dead_elephant_text = Dead_elephant_display()
map_element = mg.visualization.MapModule(infected_draw)
infected_chart = mesa.visualization.ChartModule(
    [
        {"Label": "affected", "Color": "White"},
        {"Label": "not_affected", "Color": "Green"},
        {"Label": "harm", "Color": "Red"},
        {"Label": "not_harm", "Color": "Black"},
        {"Label": "dead", "Color": "White"}
    ]
)
server = mesa.visualization.ModularServer(
    GeoSir,
    [dead_people_text, dead_elephant_text, map_element, infected_chart],
    "Human Elephant Conflict Model",
    model_params,
)
# 
