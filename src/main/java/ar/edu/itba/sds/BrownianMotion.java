package ar.edu.itba.sds;

import ar.edu.itba.sds.objects.Event;
import ar.edu.itba.sds.objects.Particle;

import java.io.*;
import java.util.*;

public class BrownianMotion {
    private static final String DEFAULT_STATIC = "static.txt";
    private static final String DEFAULT_DYNAMIC = "dynamic.txt";
    private static final int DEFAULT_MAX_EVENTS = 100;

    private static final String STATIC_PARAM = "static";
    private static final String DYNAMIC_PARAM = "dynamic";

    private static final int ERROR_STATUS = 1;

    private static String staticFilename, dynamicFilename;
    private static int N;
    private static double L;
    private static double time = 0.0;

    public static void main(String[] args) {
        try {
            argumentParsing();
        } catch (ArgumentException e) {
            System.err.println(e.getMessage());
            System.exit(ERROR_STATUS);
            return;
        }

        // Measure file reading time
        long startTime = System.currentTimeMillis();

        // Parse static file
        double[] particleRadius, particleMass;
        try(BufferedReader reader = new BufferedReader(new FileReader(staticFilename))) {
            N = Integer.parseInt(reader.readLine());
            L = Double.parseDouble(reader.readLine());

            particleRadius = new double[N];
            particleMass = new double[N];

            // Fill radius and mass arrays
            fillProperties(reader, particleRadius, particleMass);

        } catch (FileNotFoundException e) {
            System.err.println("Static file not found");
            System.exit(ERROR_STATUS);
            return;
        } catch (IOException e) {
            System.err.println("Error reading static file");
            System.exit(ERROR_STATUS);
            return;
        }

        // Parse dynamic file
        List<Particle> particles;
        try(BufferedReader reader = new BufferedReader(new FileReader(dynamicFilename))) {
            // Set initial time
            time = Double.parseDouble(reader.readLine());
            // Create particle list
            particles = createParticleList(reader, particleRadius, particleMass);
        } catch (FileNotFoundException e) {
            System.err.println("Dynamic file not found");
            System.exit(ERROR_STATUS);
            return;
        } catch (IOException e) {
            System.err.println("Error dynamic static file");
            System.exit(ERROR_STATUS);
            return;
        }

        long endTime = System.currentTimeMillis();
        System.out.printf("File parsing time \t\t ⏱  %g seconds\n", (endTime - startTime) / 1000.0);

        // Simulation
        final Queue<Event> eventQueue = createQueueFromList(particles);
        // TODO: Check criterio de corte
        int eventsTriggered = 0;
        while (!eventQueue.isEmpty() && eventsTriggered < DEFAULT_MAX_EVENTS) {
            final Event event = eventQueue.poll();
            if (event.isValid()) {
                final double eventTime = event.getTime();
                // Advance all particles delta t
                particles.forEach(p -> p.advanceTime(eventTime - time));
                time = eventTime;
                // Write particle state to dynamic file
                // TODO: Check si esto va antes o despues de hacer el evento
                try {
                    writeParticleState(particles);
                } catch (IOException e) {
                    System.err.println("Error writing dynamic file");
                    System.exit(ERROR_STATUS);
                    return;
                }
                // Update colliding particles velocities
                event.performEvent();
                // Determine future collisions
                addFutureCollisions(eventQueue, event.getParticle1(), particles); // If p1 collides with p2, it will be added twice
                addFutureCollisions(eventQueue, event.getParticle2(), particles); // Second time will be invalid when triggered
                // Add one to counter
                eventsTriggered++;
            }
        }
    }

    private static void addFutureCollisions(Queue<Event> queue, Particle particle, List<Particle> particles) {
        if (particle == null) return;

        // Create vertical wall collision event
        Double tc = particle.collidesX(0, L);
        if (tc != null) queue.add(new Event(time + tc, particle, true));

        // Create horizontal wall collision event
        tc = particle.collidesY(0, L);
        if (tc != null) queue.add(new Event(time + tc, particle, false));

        for (Particle other : particles) {
            tc = particle.collides(other);
            if (tc != null) queue.add(new Event(time + tc, particle, other));
        }
    }

    private static void writeParticleState(List<Particle> particles)
            throws IOException {
        StringBuilder sb = new StringBuilder();
        sb.append(String.format("*\n%.7E\n", time));
        particles.forEach(p -> sb.append(String.format("%.7E %.7E %.7E %.7E\n", p.getX(), p.getY(), p.getVx(), p.getVy())));

        try(BufferedWriter writer = new BufferedWriter(new FileWriter(dynamicFilename, true))) {
            writer.write(sb.toString());
        }
    }

    private static Queue<Event> createQueueFromList(List<Particle> particles) {
        final Queue<Event> eventQueue = new PriorityQueue<>();
        Double tc;
        for (int i = 0; i < particles.size(); i++) {
            Particle cur = particles.get(i);
            // Create vertical wall collision event
            tc = cur.collidesX(0, L);
            if (tc != null) eventQueue.add(new Event(time + tc, cur, true));

            // Create horizontal wall collision event
            tc = cur.collidesY(0, L);
            if (tc != null) eventQueue.add(new Event(time + tc, cur, false));

            // Create two particle collision events
            for (int j = i + 1; j < particles.size(); j++) {
                Particle other = particles.get(j);
                tc = cur.collides(other);
                if (tc != null) eventQueue.add(new Event(time + tc, cur, other));
            }
        }
        return eventQueue;
    }

    private static List<Particle> createParticleList(BufferedReader reader, double[] radiusArray, double[] massArray)
            throws IOException {
        if (radiusArray.length != massArray.length) throw new IllegalArgumentException("Radius and mass array must be same sized!");

        List<Particle> particles = new ArrayList<>();

        for (int i = 0; i < radiusArray.length; i++) {
            String line = reader.readLine();
            if (line == null) throw new IOException();

            // Values has format (x, y, vx, vy)
            final String[] values = line.split(" ");
            double x = Double.parseDouble(values[0]), y = Double.parseDouble(values[1]);
            double vx = Double.parseDouble(values[2]), vy = Double.parseDouble(values[3]);

            particles.add(new Particle(i, x, y, vx, vy, radiusArray[i], massArray[i]));
        }

        return particles;
    }

    private static void fillProperties(BufferedReader reader, double[] radiusArray, double[] massArray)
            throws IOException {
        if (radiusArray.length != massArray.length) throw new IllegalArgumentException("Radius and mass array must be same sized!");

        for (int i = 0; i < radiusArray.length; i++) {
            String line = reader.readLine();
            if (line == null) throw new IOException();

            String[] props = line.split(" ");
            radiusArray[i] = Double.parseDouble(props[0]);
            massArray[i] = Double.parseDouble(props[1]);
        }
    }

    private static void argumentParsing() throws ArgumentException {
        Properties properties = System.getProperties();

        staticFilename = properties.getProperty(STATIC_PARAM, DEFAULT_STATIC);
        dynamicFilename = properties.getProperty(DYNAMIC_PARAM, DEFAULT_DYNAMIC);
    }
}
