import mesa
import mesa_geo as mg
from shapely.geometry import Point

from agents import PersonAgent, ElephantAgent, NeighbourhoodAgent


class GeoSir(mesa.Model):
    """Model class for a simplistic infection model.
    
    The agent is created in the agent class and agent is added to space and the schecule here.
    """

    # Geographical parameters for desired map
    geojson_regions = "data/testing_to_apply.geojson"
    #geojson_regions = "data/somawathiya_gjson.geojson"
    unique_id = "id"

    def __init__(
        self, elephant_pop_size=30, human_pop_size=30, init_affected=0.2, init_harm=0.2, exposure_distance=10, affected_risk=0.2, harm_risk=0.2, number_of_steps=500
    ):
        """
        Create a new InfectedModel
        :param pop_size:        Size of population
        :param init_infected:   Probability of a person agent to start as infected
        :param exposure_distance:   Proximity distance between agents to be exposed to each other
        :param infection_risk:      Probability of agent to become infected, if it has been exposed to another infected
        """
        #self.schedule = mesa.time.BaseScheduler(self) # <-------------- this can be randomly activated
        self.schedule = mesa.time.RandomActivation(self) # <---------- randomly activating
        self.space = mg.GeoSpace(warn_crs_conversion=False)
        self.steps = 0
        self.counts = None
        self.reset_counts()

        # SIR model parameters
        self.human_pop_size = human_pop_size
        self.elephant_pop_size = elephant_pop_size
        self.counts["not_affected"] = human_pop_size
        self.exposure_distance = exposure_distance
        self.affected_risk = affected_risk
        self.harm_risk = harm_risk
        self.number_of_steps = number_of_steps

        self.running = True
        self.datacollector = mesa.DataCollector(
            {
                "affected": get_affected_count,
                "not_affected": get_not_affected_count,
                "harm": get_harm_count,
                "not_harm": get_not_harm_count,
                "dead": get_dead_count,
            }
        )
        # /////////////////////////////////////////////////////////////////////////////////////////

        # Set up the Neighbourhood patches for every region in file (add to schedule later)
        ac = mg.AgentCreator(NeighbourhoodAgent, model=self)
        neighbourhood_agents = ac.from_file(self.geojson_regions, unique_id=self.unique_id)   

        self.space.add_agents(neighbourhood_agents)
        # //////////////////////////////////////////////////////////////////////////////////////////
        # Generate PersonAgent population

        ac_population = mg.AgentCreator(
            PersonAgent,
            model=self,
            crs=self.space.crs,
            agent_kwargs={"init_affected": init_affected},
        )
        
        elepnat_population = mg.AgentCreator(
            ElephantAgent,
            model=self,
            crs=self.space.crs,
            agent_kwargs={"init_harm": init_harm},
        )
        # //////////////////////////////////////////////////////////////////////////////////////////

        """ getting the centroids of the segmented areas """
        """segmented_areas = {}
        for i in neighbourhood_agents: 
            id = i.unique_id   
            segmented_areas[id] = i.geometry.centroid.coords.xy 
            center_x, center_y = i.geometry.centroid.coords.xy
        print(segmented_areas)""" 

        """ getting the bounds of the segmented areas """
        """segmented_areas_boundaries = {}
        for i in neighbourhood_agents: 
            id = i.unique_id   
            this_bounds = i.geometry.bounds
            segmented_areas_boundaries[id] = this_bounds

        print(segmented_areas_boundaries)"""

        # Generate random location, add agent to grid and scheduler
        for i in range(self.elephant_pop_size):    
            ######this_neighbourhood = self.random.randint(0, len(neighbourhood_agents) - 1) 

            for neighbourhood_agent in neighbourhood_agents:
                # 0 is for the forests
                if neighbourhood_agent.unique_id == 0:
                    this_neighbourhood = neighbourhood_agent
            # Region where agent starts
            ####center_x, center_y = neighbourhood_agents[this_neighbourhood].geometry.centroid.coords.xy
            center_x, center_y = this_neighbourhood.geometry.centroid.coords.xy
            
            # Heuristic for agent spread in region
            ####this_bounds = neighbourhood_agents[this_neighbourhood].geometry.bounds
            this_bounds = this_neighbourhood.geometry.bounds
            spread_x = int(this_bounds[2] - this_bounds[0])  
            spread_y = int(this_bounds[3] - this_bounds[1])
            
            this_x = center_x[0] + self.random.randint(0, spread_x) - spread_x / 2
            this_y = center_y[0] + self.random.randint(0, spread_y) - spread_y / 2

            this_elephant = elepnat_population.create_agent(Point(this_x, this_y), "E" + str(i))

            self.space.add_agents(this_elephant)
            self.schedule.add(this_elephant)

        for i in range(self.human_pop_size):    
            #this_neighbourhood = self.random.randint(0, len(neighbourhood_agents) - 1) 
            for neighbourhood_agent in neighbourhood_agents:
                # 0 is for the forests
                if neighbourhood_agent.unique_id == 4:
                    this_neighbourhood = neighbourhood_agent
            # Region where agent starts
            center_x, center_y = this_neighbourhood.geometry.centroid.coords.xy
            
            # Heuristic for agent spread in region
            this_bounds = this_neighbourhood.geometry.bounds

            spread_x = int(this_bounds[2] - this_bounds[0])  
            spread_y = int(this_bounds[3] - this_bounds[1])
            
            this_x = center_x[0] + self.random.randint(0, spread_x) - spread_x / 2
            this_y = center_y[0] + self.random.randint(0, spread_y) - spread_y / 2
           
            this_person = ac_population.create_agent(Point(this_x, this_y), "P" + str(i))
            
            self.space.add_agents(this_person)
            self.schedule.add(this_person)

        # Add the neighbourhood agents to schedule AFTER person agents,
        # to allow them to update their color by using BaseScheduler
        """for agent in neighbourhood_agents:
            self.schedule.add(agent)"""

        self.datacollector.collect(self)

    def reset_counts(self):
        self.counts = {
            "affected": 0,
            "not_affected": 0,
            "harm": 0,
            "not_harm": 0,
            "safe": 0,
            "hotspot": 0,
            "dead": 0,
        }

    def step(self):
        """Run one step of the model."""
        self.steps += 1
        self.reset_counts()
        self.schedule.step()
        self.space._recreate_rtree()  # Recalculate spatial tree, because agents are moving
        self.datacollector.collect(self)

        # Run until everyone is affected  <----------- this has to be changed
        if self.steps == self.number_of_steps:
            self.running = False


# Functions needed for datacollector
def get_affected_count(model):
    return model.counts["affected"]


def get_not_affected_count(model):
    return model.counts["not_affected"]


def get_harm_count(model):
    return model.counts["harm"]


def get_not_harm_count(model):
    return model.counts["not_harm"]

def get_dead_count(model):
    return model.counts["dead"]    
