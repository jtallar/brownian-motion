import math
import statistics as sts

class Particle(object):

    def __init__(self, id, x=0, y=0, vx=0, vy=0, r=0, m=0):
        """Returns a Particle object with the given coordinates

        Parameters
        ----------
        id : int
            Particle id
        x : float
            Horizontal coordinate
        y : float
            Vertical coordinate
        vx : float
            Horizontal speed
        vy : float
            Vertical speed
        r : float
            Particle radius
        m : float
            Particle mass
        """

        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.r = r
        self.m = m

    def center_distance(self, other):
        return math.sqrt(math.pow(self.x - other.x, 2) + math.pow(self.y - other.y, 2))

    def border_distance(self, other):
        return self.center_distance(other) - self.r - other.r

    def get_point(self):
        return (self.x, self.y)

    def get_v_mod(self):
        return (self.vx * self.vx + self.vy * self.vy) ** 0.5

    def collides_with_wall(self, side):
        # 5.8000000E+00 --> Check if it counts all digits
        return (self.x + self.r) >= side or (self.y + self.r) >= side or (self.x - self.r) <= 0.0 or (self.y - self.r) <= 0.0

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Particle %s(%.2f,%.2f; r=%.2f)" % (self.id, self.x, self.y, self.r)

    # Define hash and eq methods to allow key usage
    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __ne__(self, other):
        return not (self == other)

class ParticleNode(object):

    def __init__(self, particle, next=None):
        """Returns a Particle object with the given coordinates

        Parameters
        ----------
        particle : Particle
            Particle in node
        next : Particle
            Next particle in list
        """

        self.particle = particle
        self.next = next

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Node{%s, next=%s}" % (self.particle, self.next)

class Metrics(object):
    def __init__(self, N, L, kinetic_energy, big_position_x_list, big_position_y_list, collision_count, collision_freq, avg_intercollision_time, small_dcm_D, big_z_dist_list, big_z_dist_time_list):
        self.N = N
        self.L = L
        self.kinetic_energy = kinetic_energy
        self.big_position_x_list = big_position_x_list
        self.big_position_y_list = big_position_y_list
        self.collision_count = collision_count
        self.collision_freq = collision_freq
        self.avg_intercollision_time = avg_intercollision_time
        self.small_dcm_D = small_dcm_D
        self.big_z_dist_list = big_z_dist_list
        self.big_z_dist_time_list = big_z_dist_time_list

    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (self.N, self.L, self.kinetic_energy, "self.big_position_x_list", "self.big_position_y_list", self.collision_count, self.collision_freq, self.avg_intercollision_time, self.small_dcm_D, "self.big_z_dist_list", "self.big_z_dist_time_list")

class FullValue(object):
    def __init__(self, media, std):
        if std == 0:
            self.dec_count = 3
        else:
            exp = math.ceil(math.log10(std))
            self.dec_count = abs(exp) if exp < 0 else 0
        self.media = round(media, self.dec_count)
        self.std = round(std, self.dec_count)
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return "%s±%s" % (self.media, self.std)

class Summary(object):
    def __init__(self, metric_list, param, big_dcm=True):
        self.param = param
        collision_count_list = []
        collision_freq_list = []
        avg_intercollision_time_list = []
        small_dcm_D_list = []
        kinetic_energy_list = []
        big_z_dist_superlist = []
        big_z_dist_time_superlist = []

        for metric in metric_list:
            # Save last values for some params
            self.N = metric.N
            self.L = metric.L
            self.last_kinetic_energy = metric.kinetic_energy
            self.big_position_x_list = metric.big_position_x_list
            self.big_position_y_list = metric.big_position_y_list
            
            # Save all params to create Full Values later
            collision_count_list.append(metric.collision_count)
            collision_freq_list.append(metric.collision_freq)
            avg_intercollision_time_list.append(metric.avg_intercollision_time)
            small_dcm_D_list.append(metric.small_dcm_D)
            kinetic_energy_list.append(metric.kinetic_energy)
            
            big_z_dist_superlist.append(metric.big_z_dist_list)
            big_z_dist_time_superlist.append(metric.big_z_dist_time_list)

        # Create Full values for lists
        self.collision_count = FullValue(sts.mean(collision_count_list), sts.stdev(collision_count_list))
        self.collision_freq = FullValue(sts.mean(collision_freq_list), sts.stdev(collision_freq_list))
        self.avg_intercollision_time = FullValue(sts.mean(avg_intercollision_time_list), sts.stdev(avg_intercollision_time_list))
        self.small_dcm_D = FullValue(sts.mean(small_dcm_D_list), sts.stdev(small_dcm_D_list))
        self.kinetic_energy = FullValue(sts.mean(kinetic_energy_list), sts.stdev(kinetic_energy_list))

        # Leave everything to calculate big_dcm_D from superlists
        self.big_dcm_list = []
        self.big_dcm_time_list = []
        if big_dcm:
            self.build_big_dcm(big_z_dist_superlist, big_z_dist_time_superlist)
    
    def build_big_dcm(self, big_z_dist_superlist, big_z_dist_time_superlist):
        big_collided = False
        time_index = 0
        while not big_collided:
            big_z_dist_sq_sum = 0
            cur_time_sum = 0
            for i in range(len(big_z_dist_superlist)):
                if time_index >= len(big_z_dist_superlist[i]):
                    big_collided = True
                    break
                big_z_dist_sq_sum += big_z_dist_superlist[i][time_index] ** 2
                cur_time_sum += big_z_dist_time_superlist[i][time_index]
            
            if not big_collided:
                self.big_dcm_list.append(big_z_dist_sq_sum / len(big_z_dist_superlist))
                self.big_dcm_time_list.append(cur_time_sum / len(big_z_dist_superlist))

            time_index += 1        

    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return ""