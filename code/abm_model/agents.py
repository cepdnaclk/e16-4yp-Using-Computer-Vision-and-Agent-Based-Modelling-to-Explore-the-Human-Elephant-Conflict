from shapely.geometry import Point
from numpy import random
import numpy as np
import mesa_geo as mg
import math
import random as r

areas_centroids = {
                    0: (9051869.984199457, 715075.9205322468), 
                    1: (9052468.895260904, 714837.0948350684), 
                    2: (9053010.982222058, 714949.7852888558), 
                    3: (9054015.2659388, 714952.531727569), 
                    4: (9054092.613024183, 715429.2137873578)
                  }

areas_bounds = {
                0: (9051231.256505975, 713781.3815231089, 9052881.46170866, 716040.2689726875), 
                1: (9051826.412480716, 713781.3815231089, 9053052.79448927, 715954.602582385), 
                2: (9052552.322419604, 714462.20388815, 9053440.54762433, 715490.2005717931), 
                3: (9053404.477565257, 714642.5541835276, 9054775.139810106, 715318.8677911856), 
                4: (9053751.651883854, 715251.2364304201, 9054473.053065352, 715616.4457785554)
               }                  

social_impact = random.poisson(lam=8, size=30)
social_impact = social_impact + 10

economy_impact = random.poisson(lam=12, size=30)
economy_impact = economy_impact + 10 

elephant_gender = random.poisson(lam=12, size=30)

have_babies = random.poisson(lam=12, size=30)



class PersonAgent(mg.GeoAgent):
    """
    Person Agent. so these are the infected or uninfected agents  
    giving random knowledge to people. 

    params:
        economic_impact : this is the wealth the persons have       : probability distributions
        social_impact : this is how the social knowledge they have  : probability distributions

        (economic_impact x a) + (social_impact x b) = distance_between_agent_and_forest_boundary

        *                                                                         ######
       ***  <--------- distance_between_agent_and_forest_boundary -------------> ######
        *                                                                         ######
                                                                                 ######
    """
    

    def __init__(
        self,
        unique_id,
        model,
        geometry,
        crs,
        agent_type="not_affected",
        init_affected=0.1,
        mobility_range=10,
    ):
        """
        Create a new person agent.
        :param unique_id:   Unique identifier for the agent
        :param model:       Model in which the agent runs
        :param geometry:    Shape object for the agent
        :param agent_type:  Indicator if agent is infected ("infected", "susceptible", "recovered" or "dead")
        :param mobility_range:  Range of distance to move in one step
        """
        super().__init__(unique_id, model, geometry, crs)
        # Agent parameters
        self.atype = agent_type
        self.mobility_range = mobility_range

        # Random choose if infected
        #if self.random.random() < init_affected:
            #self.atype = "affected"
            #self.model.counts["affected"] += 1  # Adjust initial counts
            #self.model.counts["not_affected"] -= 1 # reduce the susceptible person as one has the diseases

        """ this is the centroids of the segmented areas - hardcoded """
          

        self.random_num_social_impact = random.choice(social_impact)
        self.random_num_economy_impact = random.choice(economy_impact)

        self.random_val_movement = self.random_num_social_impact + (2 * self.random_num_economy_impact)
        self.go_towards_forest_area = 0
        self.go_towards_cultivation_area = 0

        if self.random_val_movement < 55:
            self.go_towards_forest_area = 1
        elif self.random_val_movement > 55 and self.random_val_movement < 65:
            self.go_towards_cultivation_area = 1    

        self.no_of_steps = 0
        self.steps_list = []  
        self.life_level = 0  

    def move_point(self, dx, dy):
        """
        Move a point by creating a new one
        :param dx:  Distance to move in x-axis
        :param dy:  Distance to move in y-axis
        """

        # moving towards the forest area
        f_c_x, f_c_y = areas_centroids[0]
        f_c_1 = [f_c_x, f_c_y]
        f_l_1 = [self.geometry.x + dx, self.geometry.y + dy]
        f_l_2 = [self.geometry.x, self.geometry.y]
        f_d_1 = (math.dist(f_l_1, f_c_1))
        f_d_2 = (math.dist(f_l_2, f_c_1))

        # moving towards the forest area
        c_c_x, c_c_y = areas_centroids[3]
        c_c_1 = [c_c_x, c_c_y]
        c_l_1 = [self.geometry.x + dx, self.geometry.y + dy]
        c_l_2 = [self.geometry.x, self.geometry.y]
        c_d_1 = (math.dist(c_l_1, c_c_1))
        c_d_2 = (math.dist(c_l_2, c_c_1))

        x_1, y_1, x_2, y_2 = areas_bounds[2][0], areas_bounds[2][1], areas_bounds[2][2], areas_bounds[2][3]
        if x_1 > x_2:
            s_x = x_2
            e_x = x_1
        else:
            s_x = x_1
            e_x = x_2

        if y_1 > y_2:
            s_y = y_2
            e_y = y_1
        else:
            s_y = y_1
            e_y = y_2

        inside_area = 0    
            
        if (self.geometry.x + dx > s_x and self.geometry.x + dx < e_x) and (self.geometry.y + dy > s_y and self.geometry.y + dy < e_y):
            inside_area = 1

        if inside_area == 0:
            if self.go_towards_forest_area == 1:
                if f_d_1 < f_d_2:
                    return Point(self.geometry.x + dx, self.geometry.y + dy) 
                else:
                    return Point(self.geometry.x, self.geometry.y) 
            elif self.go_towards_cultivation_area == 1:
                if c_d_1 < c_d_2:
                    return Point(self.geometry.x + dx, self.geometry.y + dy) 
                else:
                    return Point(self.geometry.x, self.geometry.y)        
            else:
                return Point(self.geometry.x + dx, self.geometry.y + dy)       
        else:
            self.steps_list.append(self.no_of_steps)
                    
            if len(self.steps_list) >= 2:
                if self.steps_list[len(self.steps_list)-1] - self.steps_list[len(self.steps_list)-2] > 5 and self.steps_list[len(self.steps_list)-1] - self.steps_list[len(self.steps_list)-2] < 10:
                    self.steps_list = []

            if len(self.steps_list) == 10:
                self.steps_list = []
                if dy<0:
                    return Point(self.geometry.x + dx, self.geometry.y - 30 * dy) 
                else:
                    return Point(self.geometry.x + dx, self.geometry.y + 30 * dy)     
                
            return Point(self.geometry.x, self.geometry.y) 


    def step(self):
        """ Advance one step. <----- this has to be modified """
        # If susceptible, check if exposed 

        self.no_of_steps = self.no_of_steps + 1

        if self.atype == "not_affected":

            neighbors = self.model.space.get_neighbors_within_distance(self, self.model.exposure_distance)

            """ if neighbours are infected and has a given infection rate then the person get infected 
                within the next step
            """
            for neighbor in neighbors:
                if (neighbor.atype == "not_harm" ):
                    self.life_level = self.life_level + 1

                    if self.life_level == 10:
                        self.atype = "affected"
                        break
                elif neighbor.atype == "harm":
                    self.atype = "affected"
                    break
                else:
                    pass

        # If not dead, move
        if self.atype == "not_affected":
            move_x = self.random.randint(-self.mobility_range, self.mobility_range)
            move_y = self.random.randint(-self.mobility_range, self.mobility_range)
            self.geometry = self.move_point(move_x, move_y)  # Reassign geometry

        self.model.counts[self.atype] += 1  # Count agent type

    def __repr__(self):
        return "Person " + str(self.unique_id)

class ElephantAgent(mg.GeoAgent):
    """Elephant Agent. so these are the infected or uninfected agents  """

    def __init__(
        self,
        unique_id,
        model,
        geometry,
        crs,
        agent_type="not_harm",
        init_harm=0.1,
        mobility_range=10,
        init_musth = 15
    ):
        """
        Create a new person agent.
        :param unique_id:   Unique identifier for the agent
        :param model:       Model in which the agent runs
        :param geometry:    Shape object for the agent
        :param agent_type:  Indicator if agent is infected ("infected", "susceptible", "recovered" or "dead")
        :param mobility_range:  Range of distance to move in one step
        """
        super().__init__(unique_id, model, geometry, crs)
        # Agent parameters
        self.atype = agent_type
        self.mobility_range = mobility_range

        # Random choose if infected ---- this is for one agent
        #if self.random.random() < init_harm:
        #    self.atype = "harm"
        #    self.model.counts["harm"] += 1  # Adjust initial counts
        #    self.model.counts["not_harm"] -= 1 # reduce the susceptible person as one has the diseases

        self.gender = 0 # gender 0 : female , 1 : male
        self.musth = 0 # musth rate 0 : have no musth, 1 : have musth
        self.mother_elephant = 1 
        self.random_num_elephant_gender = random.choice(elephant_gender)
        if self.random_num_elephant_gender >= 15:
            self.gender = 1    

        if self.gender == 1:
            musth_of_elephant = r.randrange(2, 20)
            if musth_of_elephant >= init_musth:
                self.musth = 1

        if self.gender == 0:
            self.random_num_have_babies = random.choice(have_babies)
            if self.random_num_have_babies >= 15:
                self.mother_elephant = 1 

        if self.musth == 1:
            self.atype = "harm"
            self.mobility_range = 15

        if self.mother_elephant == 1:
            self.atype = "harm"  
            self.mobility_range = 8

        if self.musth == 0:
            self.atype = "not_harm"
            self.mobility_range = mobility_range

        if self.mother_elephant == 0:
            self.atype = "not_harm"  
            self.mobility_range = mobility_range

        thirsty = r.randrange(2, 20)
        self.thirsty_elephant = 0
        if thirsty >= 15:
            self.thirsty_elephant = 1

        hungry = r.randrange(2, 20)
        self.hungry_elephant = 0
        if hungry >= 15:
            self.hungry_elephant = 1    

        self.no_of_steps = 0
        self.steps_list = [] 

    def move_point(self, dx, dy):
        """
        Move a point by creating a new one
        :param dx:  Distance to move in x-axis
        :param dy:  Distance to move in y-axis
        """
        # directing thirsty elephats towards the water resources
        w_c_x, w_c_y = areas_centroids[2]
        w_c_1 = [w_c_x, w_c_y]
        w_l_1 = [self.geometry.x + dx, self.geometry.y + dy]
        w_l_2 = [self.geometry.x, self.geometry.y]

        w_moved_points = [w_l_1, w_l_2]
        w_d_1 = (math.dist(w_l_1, w_c_1))
        w_d_2 = (math.dist(w_l_2, w_c_1))

        w_distances = [w_d_1, w_d_2]
        w_array_distance = np.array(w_distances)
        w_min_index_distance = w_array_distance.argmin()

        # directing hungry elephats towards the cultivations
        c_c_x, c_c_y = areas_centroids[3]
        c_c_1 = [c_c_x, c_c_y]
        c_l_1 = [self.geometry.x + dx, self.geometry.y + dy]
        c_l_2 = [self.geometry.x, self.geometry.y]

        c_moved_points = [c_l_1, c_l_2]
        c_d_1 = (math.dist(c_l_1, c_c_1))
        c_d_2 = (math.dist(c_l_2, c_c_1))

        c_distances = [c_d_1, c_d_2]
        c_array_distance = np.array(c_distances)
        c_min_index_distance = c_array_distance.argmin()

        # directing hungry elephats towards the human areas
        h_c_x, h_c_y = areas_centroids[4]
        h_c_1 = [h_c_x, h_c_y]
        h_l_1 = [self.geometry.x + dx, self.geometry.y + dy]
        h_l_2 = [self.geometry.x, self.geometry.y]

        h_moved_points = [h_l_1, h_l_2]
        h_d_1 = (math.dist(h_l_1, h_c_1))
        h_d_2 = (math.dist(h_l_2, h_c_1))

        h_distances = [h_d_1, h_d_2]
        h_array_distance = np.array(h_distances)
        h_min_index_distance = h_array_distance.argmin()

        ##################################################################################
        x_1, y_1, x_2, y_2 = areas_bounds[2][0], areas_bounds[2][1], areas_bounds[2][2], areas_bounds[2][3]
        if x_1 > x_2:
            s_x = x_2
            e_x = x_1
        else:
            s_x = x_1
            e_x = x_2

        if y_1 > y_2:
            s_y = y_2
            e_y = y_1
        else:
            s_y = y_1
            e_y = y_2

        inside_area = 0    
        if (self.geometry.x + dx > s_x and self.geometry.x + dx < e_x) and (self.geometry.y + dy > s_y and self.geometry.y + dy < e_y):
            self.thirsty_elephant = 0
            inside_area = 1
        
        ##################################################################################
        x_1, y_1, x_2, y_2 = areas_bounds[3][0], areas_bounds[3][1], areas_bounds[3][2], areas_bounds[3][3]
        if x_1 > x_2:
            s_x = x_2
            e_x = x_1
        else:
            s_x = x_1
            e_x = x_2

        if y_1 > y_2:
            s_y = y_2
            e_y = y_1
        else:
            s_y = y_1
            e_y = y_2
   
        if (self.geometry.x + dx > s_x and self.geometry.x + dx < e_x) and (self.geometry.y + dy > s_y and self.geometry.y + dy < e_y):
            self.hungry_elephant = 0

        x_1, y_1, x_2, y_2 = areas_bounds[4][0], areas_bounds[4][1], areas_bounds[4][2], areas_bounds[4][3]
        if x_1 > x_2:
            s_x = x_2
            e_x = x_1
        else:
            s_x = x_1
            e_x = x_2

        if y_1 > y_2:
            s_y = y_2
            e_y = y_1
        else:
            s_y = y_1
            e_y = y_2
   
        if (self.geometry.x + dx > s_x and self.geometry.x + dx < e_x) and (self.geometry.y + dy > s_y and self.geometry.y + dy < e_y):
            self.hungry_elephant = 0    
        ##################################################################################
        if inside_area == 0:
            if self.thirsty_elephant == 1 and self.hungry_elephant == 0:
                dis_x, dis_y = (w_moved_points[w_min_index_distance])
                return Point(dis_x, dis_y)
            elif self.hungry_elephant == 1 and self.thirsty_elephant == 0:
                if c_moved_points[c_min_index_distance] < h_moved_points[h_min_index_distance]:
                    dis_x, dis_y = (c_moved_points[c_min_index_distance])
                    return Point(dis_x, dis_y)  
                else:
                    dis_x, dis_y = (h_moved_points[h_min_index_distance])
                    return Point(dis_x, dis_y)
            elif self.hungry_elephant == 1 and self.thirsty_elephant == 1:
                first_come = []
                """
                1:cultivation
                2:human area
                3:water resources
                """
                if c_moved_points[c_min_index_distance] < w_moved_points[w_min_index_distance]:
                    if c_moved_points[c_min_index_distance] < h_moved_points[h_min_index_distance]:
                        dis_x, dis_y = (c_moved_points[c_min_index_distance])
                        first_come.append(1)
                        return Point(dis_x, dis_y)  
                    else:
                        dis_x, dis_y = (h_moved_points[h_min_index_distance])
                        first_come.append(2)
                        return Point(dis_x, dis_y) 
                else:
                    dis_x, dis_y = (w_moved_points[w_min_index_distance])
                    first_come.append(3)
                    return Point(dis_x, dis_y)  

            else:
                return Point(self.geometry.x + dx, self.geometry.y + dy)            
        else:
            #return Point(self.geometry.x + dx, self.geometry.y + dy) 

            self.steps_list.append(self.no_of_steps)
                    
            if len(self.steps_list) >= 2:
                if self.steps_list[len(self.steps_list)-1] - self.steps_list[len(self.steps_list)-2] > 5 and self.steps_list[len(self.steps_list)-1] - self.steps_list[len(self.steps_list)-2] < 10:
                    self.steps_list = []

            if len(self.steps_list) == 10:
                self.steps_list = []
                if dy<0:
                    return Point(self.geometry.x + dx, self.geometry.y - 30 * dy) 
                else:
                    return Point(self.geometry.x + dx, self.geometry.y + 30 * dy)     
                
            return Point(self.geometry.x, self.geometry.y)  
        ##################################################################################

    def step(self):
        """Advance one step."""
        # If susceptible, check if exposed

        self.no_of_steps = self.no_of_steps + 1

        """if self.atype == "not_harm":

            neighbors = self.model.space.get_neighbors_within_distance(self, self.model.exposure_distance)
            for neighbor in neighbors:
                if (
                    neighbor.atype == "not_affected"
                    and self.random.random() < self.model.harm_risk
                ):
                    self.atype = "harm"
                    break"""

        if self.no_of_steps == 500 and self.hungry_elephant == 1 and self.thirsty_elephant == 1:
            self.atype = "dead"

        if self.atype != "dead":    
            move_x = self.random.randint(-self.mobility_range, self.mobility_range)
            move_y = self.random.randint(-self.mobility_range, self.mobility_range)
            self.geometry = self.move_point(move_x, move_y)  # Reassign geometry

        self.model.counts[self.atype] += 1  # Count agent type

    def __repr__(self):
        return "Elephant " + str(self.unique_id)        

""""""
class NeighbourhoodAgent(mg.GeoAgent):
    """Neighbourhood agent. Changes color according to number of infected inside it.
       This is the actual area
    """

    def __init__(
        self, unique_id, model, geometry, crs, agent_type="safe", hotspot_threshold=2
    ):
        """
        Create a new Neighbourhood agent.
        :param unique_id:   Unique identifier for the agent
        :param model:       Model in which the agent runs
        :param geometry:    Shape object for the agent
        :param agent_type:  Indicator if agent is infected ("infected", "susceptible", "recovered" or "dead")
        :param hotspot_threshold:   Number of infected agents in region to be considered a hot-spot
        """
        super().__init__(unique_id, model, geometry, crs)
        self.atype = agent_type

        # When a neighborhood is considered a hot-spot
        self.hotspot_threshold = (hotspot_threshold)
        self.color_hotspot()

    def step(self):
        """Advance agent one step."""
        self.color_hotspot()
        self.model.counts[self.atype] += 1  # Count agent type

    def color_hotspot(self):
        # Decide if this region agent is a hot-spot (if more than threshold person agents are infected)
        neighbors = self.model.space.get_intersecting_agents(self) # intersecting mean agents within the given region

        affected_neighbors = [
            neighbor for neighbor in neighbors if neighbor.atype == "affected"
        ]

        if len(affected_neighbors) >= self.hotspot_threshold:
            self.atype = "hotspot"
        else:
            self.atype = "safe"

    def __repr__(self):
        return "Neighborhood " + str(self.unique_id)
