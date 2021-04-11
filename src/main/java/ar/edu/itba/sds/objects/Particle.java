package ar.edu.itba.sds.objects;

public class Particle {
    private final int id;
    private double x;
    private double y;
    private double vx;
    private double vy;
    private final double r;
    private final double m;
    private int collisionCount;

    /**
     * Create a particle with radius
     * @param id particle id
     * @param x particle x coordinate
     * @param y particle y coordinate
     * @param vx particle vx velocity
     * @param vy particle vx velocity
     * @param r particle radius
     * @param m particle mass
     */
    public Particle(int id, double x, double y, double vx, double vy, double r, double m) {
        this.id = id;
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.r = r;
        this.m = m;
        this.collisionCount = 0;
    }

    public double centerDistance(Particle other) {
        return Math.sqrt(Math.pow(x - other.x, 2) + Math.pow(y - other.y, 2));
    }

    public double borderDistance(Particle other) {
        return centerDistance(other) - r - other.r;
    }


    /**
     * @return duration of time until particle collides with a vertical wall
     *         returns null if vx = 0
     */
    public Double collidesX(double leftWallX, double rightWallX) {
        if (vx > 0) return (rightWallX - r - x) / vx;
        if (vx < 0) return (leftWallX + r - x) / vx;
        return null;
    }

    /**
     * @return duration of time until particle collides with a horizontal wall
     *         returns null if vy = 0
     */
    public Double collidesY(double bottomWallY, double topWallY) {
        if (vy > 0) return (topWallY - r - y) / vy;
        if (vy < 0) return (bottomWallY + r - y) / vy;
        return null;
    }

    /**
     * @param other particle to collide with
     * @return duration of time until particle collides with other
     *         returns null if they never collide
     */
    public Double collides(Particle other) {
        // Xi = self, Xj = other
        double deltaX = other.x - this.x, deltaY = other.y - this.y;
        double deltaVX = other.vx - this.vx, deltaVY = other.vy - this.vy;
        double sigma = this.r + other.r;

        double prodDeltaR = deltaX * deltaX + deltaY * deltaY;
        double prodDeltaV = deltaVX * deltaVX + deltaVY * deltaVY;
        double prodCross = deltaVX * deltaX + deltaVY * deltaY;

        if (prodCross >= 0) return null;

        double d = prodCross * prodCross - prodDeltaV * (prodDeltaR - sigma * sigma);
        if (d < 0) return null;

        return -(prodCross + Math.sqrt(d)) / prodDeltaV;
    }

    /**
     * Update particle to simulate it bouncing off a vertical wall
     */
    public void bounceX() {
        this.vx = -this.vx;
        this.collisionCount++;
    }

    /**
     * Update particle to simulate it bouncing off a horizontal wall
     */
    public void bounceY() {
        this.vy = -this.vy;
        this.collisionCount++;
    }

    /**
     * Update particle and other simulating them bouncing off together
     * @param other particle that collides with self
     */
    public void bounce(Particle other) {
        // Xi = self, Xj = other
        double deltaX = other.x - this.x, deltaY = other.y - this.y;
        double deltaVX = other.vx - this.vx, deltaVY = other.vy - this.vy;
        double sigma = this.r + other.r;
        double prodCross = deltaVX * deltaX + deltaVY * deltaY;

        double J = (2 * this.m * other.m * prodCross) / (sigma * (this.m + other.m));
        double Jx = J * deltaX / sigma, Jy = J * deltaY / sigma;

        this.vx = this.vx + Jx / this.m;
        this.vy = this.vy + Jy / this.m;
        this.collisionCount++;

        other.vx = other.vx - Jx / other.m;
        other.vy = other.vy - Jy / other.m;
        other.collisionCount++;
    }

    public int getCollisionCount() {
        return collisionCount;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Particle)) return false;
        Particle molecule = (Particle) o;
        return Double.compare(molecule.x, x) == 0 && Double.compare(molecule.y, y) == 0;
    }

    @Override
    public int hashCode() {
        return Double.hashCode(x) * 31 + Double.hashCode(y);
    }

    @Override
    public String toString() {
        return "Particle{" +
                "id=" + id +
                ", x=" + x +
                ", y=" + y +
                ", vx=" + vx +
                ", vy=" + vy +
                ", r=" + r +
                ", m=" + m +
                '}';
    }
}