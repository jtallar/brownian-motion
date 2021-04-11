import math

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

    # Define distance methods for multidirectional distance in a square
    def multidir_center_distance(self, other, side):
        total = 0
        for i, (a, b) in enumerate(zip(self.get_point(), other.get_point())):
            delta = abs(b - a)
            if delta > side - delta:
                delta = side - delta
            total += math.pow(delta, 2)
        return math.sqrt(total)

    def multidir_border_distance(self, other, side):
        return self.multidir_center_distance(other, side) - self.r - other.r

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