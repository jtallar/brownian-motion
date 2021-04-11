package ar.edu.itba.sds.objects;

public class Event implements Comparable<Event> {
    private final double time;
    private final Particle particle1;
    private final Particle particle2;
    private final EventType type;

    private final int collisionCount1, collisionCount2;

    /**
     * General constructor to work as helper
     * @param time time of collision
     * @param particle1 first particle to collide
     * @param particle2 second particle to collide (can be null)
     * @param type type of collision
     */
    private Event(double time, Particle particle1, Particle particle2, EventType type) {
        this.time = time;
        this.particle1 = particle1;
        this.particle2 = particle2;
        this.type = type;

        this.collisionCount1 = particle1.getCollisionCount();
        this.collisionCount2 = particle2 != null ? particle2.getCollisionCount() : 0;
    }

    /**
     * Create event involving two particles
     * @param time time of collision
     * @param particle1 first particle to collide
     * @param particle2 second particle to collide
     */
    public Event(double time, Particle particle1, Particle particle2) {
        this(time, particle1, particle2, EventType.TWO_PARTICLES);
    }

    /**
     * Create event involving a single particle and a wall
     * @param time time of collision
     * @param particle1 particle to collide
     * @param vertical true if collision with vertical wall; false if collision with horizontal wall
     */
    public Event(double time, Particle particle1, boolean vertical) {
        this(time, particle1, null, vertical ? EventType.VERTICAL_WALL : EventType.HORIZONTAL_WALL);
    }

    public double getTime() {
        return time;
    }

    public Particle getParticle1() {
        return particle1;
    }

    public Particle getParticle2() {
        return particle2;
    }

    public EventType getType() {
        return type;
    }

    /**
     * @return true if the event HAS NOT been invalidated since creation
     *         false if the event HAS been invalidated since creation
     */
    public boolean isValid() {
        int curCollisionCount1 = particle1.getCollisionCount();
        int curCollisionCount2 = particle2 != null ? particle2.getCollisionCount() : 0;

        return curCollisionCount1 == this.collisionCount1 &&
                curCollisionCount2 == this.collisionCount2;
    }

    @Override
    public int compareTo(Event o) {
        return Double.compare(time, o.time);
    }

    enum EventType {
        VERTICAL_WALL,
        HORIZONTAL_WALL,
        TWO_PARTICLES
    }

}
