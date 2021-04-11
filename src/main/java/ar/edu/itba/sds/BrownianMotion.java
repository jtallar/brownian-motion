package ar.edu.itba.sds;

import ar.edu.itba.sds.objects.Particle;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

public class BrownianMotion {
    private static final String DEFAULT_STATIC = "static.txt";
    private static final String DEFAULT_DYNAMIC = "dynamic.txt";

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
            System.err.println("Static file not found");
            System.exit(ERROR_STATUS);
            return;
        } catch (IOException e) {
            System.err.println("Error reading static file");
            System.exit(ERROR_STATUS);
            return;
        }

        long endTime = System.currentTimeMillis();
        System.out.printf("File parsing time \t\t ⏱  %g seconds\n", (endTime - startTime) / 1000.0);
        System.out.println(particles);
        // TODO: Do simulation
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
