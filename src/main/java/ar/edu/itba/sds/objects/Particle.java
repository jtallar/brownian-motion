package ar.edu.itba.sds.objects;

public class Particle {
    private final int id;
    private final double x;
    private final double y;
    private final double vx;
    private final double vy;
    private final double r;
    private final double m;

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
    }

    public double centerDistance(Particle other) {
        return Math.sqrt(Math.pow(x - other.x, 2) + Math.pow(y - other.y, 2));
    }

    public double borderDistance(Particle other) {
        return centerDistance(other) - r - other.r;
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