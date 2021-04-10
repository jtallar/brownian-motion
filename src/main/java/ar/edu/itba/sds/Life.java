package ar.edu.itba.sds;

import ar.edu.itba.sds.objects.Point3D;

import java.io.*;
import java.util.List;
import java.util.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.BiPredicate;
import java.util.function.IntConsumer;
import java.util.function.Predicate;
import java.util.stream.IntStream;

// TODO errors append some context
public class Life {
    private static final int ERROR_STATUS = 1;
    private static final String DEFAULT_SIDE = "100";
    private static final String DEFAULT_DIMENSION = "2";
    private static final String DEFAULT_INITIAL_SIDE = "40";
    private static final String DEFAULT_OCCUPATION = "60";
    private static final String DEFAULT_OUT_FILE = "data";
    private static final String DEFAULT_RULE = "=.2.|.=.3/=.3";
    private static final String DEFAULT_MOORE = "1";

    private static int matrixSide;
    private static int dimensions;
    private static HashSet<Point3D> aliveCells;
    private static String outFileName;
    private static long steps;
    private static boolean parallel;
    private static boolean center;
    private static BiPredicate<Boolean, Integer> bsPredicate;
    private static Predicate<Point3D> edgePredicate;
    private static List<Point3D> mooreNeighbours;

    public static void main(String[] args) {

        long startTime = System.currentTimeMillis();

        // initializes matrixSide and aliveCells
        initializeMatrixValues();

        // initialize the steps, out file name and parallel
        initializeVarious();

        // initialize the filter condition for a cell to live or die
        initializeFilterCondition();

        // initializes the edge condition for stop criteria
        initializeEdgeCondition();

        // initializes the cell neighbours
        initializeMooreNeighbours();

        long endTime = System.currentTimeMillis();
        System.out.printf("Life Game Processing time \t\t ⏱  %g seconds\n", (endTime - startTime) / 1000.0);
        startTime = endTime;




        // set with the hashes of the alive cells hash set
        // Key --> aliveCells.hashCode()
        // Value --> List of sets with given hashCode
        final Map<Integer, List<Set<Point3D>>> mapHashes = new HashMap<>();

        // flag for stop criteria, true if a live cell reaches the edges
        final AtomicBoolean gotToEdge = new AtomicBoolean(false);

        // as an auxiliary list, to save the next step living cells
        final List<Point3D> newList = Collections.synchronizedList(new ArrayList<>());

        // quantity of cells
        final int cellCount = (int) Math.pow(matrixSide, dimensions);




        // the consumer applied on each cell
        final IntConsumer consumer = cell -> {
            // get values
            Point3D me = new Point3D(cell, matrixSide);
            int aliveNeighbours = getAliveNeighbours(aliveCells, me);
            boolean imAlive = aliveCells.contains(me);

            // if the predicate is met, the new cell is going to live for the next iterations
            if (bsPredicate.test(imAlive, aliveNeighbours)) {
                newList.add(me);
                // if i was alive then already was a valid cell. also set only if true
                if (!imAlive && edgePredicate.test(me)) gotToEdge.set(true);
            }
        };

        // check if the stream is parallel or not
        final Runnable runnable;
        if (parallel) runnable = () -> IntStream.range(0, cellCount).parallel().forEach(consumer);
        else runnable = () -> IntStream.range(0, cellCount).forEach(consumer);




        // life game iteration until steps are over or stop criteria is met
        long i = 0;
        while (i < steps) {

            // print to the output the living cells
            printAliveCells(aliveCells, outFileName);

            // stop criteria
            if (aliveCells.size() == 0) break; // all cells dead
            if (!addToHashes(mapHashes, aliveCells)) break; // repeated state
            if (gotToEdge.get()) break; // a cell or more got to an edge

            // iterate over all possible cells
            runnable.run();

            // save the new cells to the set
            aliveCells.clear();
            aliveCells.addAll(newList);
            newList.clear();
            i++;
        }
        // end of steps




        endTime = System.currentTimeMillis();
        System.out.printf("Life Game Execution time \t\t ⏱  %g seconds\n", (endTime - startTime) / 1000.0);
        System.out.printf("\nLife Game Finished in %d steps\n", i);
        System.out.print("\nLife Game Finished due to ");
        if (aliveCells.size() == 0) System.out.print("all dead cells 💀️");
        else if (gotToEdge.get()) System.out.print("a reach on the edge \uD83C\uDFC1");
        else if (steps == i) System.out.print("reach of top steps 🪜");
        else System.out.print("a repeated stat️e \uD83D\uDD01");
        System.out.println("\n");
    }

    /**
     * @param map map instance with previous states
     * @param cells current alive cells
     * @return true if cells added to map. false otherwise.
     */
    protected static boolean addToHashes(Map<Integer, List<Set<Point3D>>> map, Set<Point3D> cells) {
        int hashCode = cells.hashCode();
        final List<Set<Point3D>> list;
        // If map does not have hashCode as key, no repetition
        if (map.containsKey(hashCode)) {
            // Iterate over known lists to check for repetition
            list = map.get(hashCode);
            for (Set<Point3D> set : list) {
                boolean contains = true;
                for (Point3D point : cells) {
                    if (!set.contains(point)) {
                        contains = false;
                        break;
                    }
                }
                // Found repeated
                if (contains) return false;
            }
        } else list = new ArrayList<>();

        // No repeated set found
        list.add(new HashSet<>(cells));
        map.put(hashCode, list);
        return true;
    }

    /**
     * Initializes the matrix side value and the set of alive cells
     */
    protected static void initializeMatrixValues() {

        final Properties properties = System.getProperties();

        // if centers the output
        center = Boolean.parseBoolean(properties.getProperty("center"));

        // if an existing file is provided for the initialization, the rest is not taken into account
        final String existingInit = properties.getProperty("in");

        if (existingInit != null) {
            // initial matrix size, dimension and alive cells
            initializeMatrixVarsFromFile(existingInit);
            aliveCells = initializeMatrixFromFile(existingInit);

        } else {

            try {
                // initial matrix size
                matrixSide = Integer.parseInt(properties.getProperty("size", DEFAULT_SIDE));

                dimensions = Integer.parseInt(properties.getProperty("dim", DEFAULT_DIMENSION));

                // region size to be set out as initial zone has to be par or not according to initial matrix size
                final int initialMatrixSide = Integer.parseInt(properties.getProperty("init", DEFAULT_INITIAL_SIDE));

                // occupation percentage level of initial zone
                final int initialOccupationPercentage = Integer.parseInt(properties.getProperty("fill", DEFAULT_OCCUPATION));

                // seed for random generated positions
                final long randomSeed = Long.parseLong(properties.getProperty("seed", String.valueOf(System.nanoTime())));

                // initialize with a random value the matrix
                aliveCells = initializeMatrixRandom(matrixSide, dimensions, initialMatrixSide, initialOccupationPercentage, randomSeed);

            } catch (NumberFormatException e) { printAndExit(e.getMessage()); }
        }
    }


    /**
     * Initializes the stop criteria and out filename for the algorithm
     */
    protected static void initializeVarious() {
        final Properties properties = System.getProperties();

        try {
            // steps stop criteria
            steps = Long.parseLong(properties.getProperty("steps", String.valueOf(Long.MAX_VALUE)));
        } catch (NumberFormatException e) { printAndExit(e.getMessage()); }

        // if runs parallel or not
        parallel = Boolean.parseBoolean(properties.getProperty("pel"));

        // if there is already a file append there
        if (properties.getProperty("in") != null) {
            outFileName = properties.getProperty("in");
            return;
        }

        // filename output prefix with the cells
        outFileName = properties.getProperty("out", DEFAULT_OUT_FILE);

        // create the file
        try(BufferedWriter writer = new BufferedWriter(new FileWriter(outFileName))) {
            writer.write(dimensions + "\n" + matrixSide + "\n");
        } catch (IOException e) { printAndExit(e.getMessage()); }
    }


    /**
     * Initializes the filter criteria for kill or live cells
     */
    protected static void initializeFilterCondition() {

        final Properties properties = System.getProperties();

        final String rule = properties.getProperty("rule", DEFAULT_RULE);

        final String[] survival = rule.split("/")[0].split("\\.");
        final String[] birth = rule.split("/")[1].split("\\.");

        Predicate<Integer> survivalPredicate = generatePredicate(survival);
        Predicate<Integer> birthPredicate = generatePredicate(birth);

        // generate the used predicate
        bsPredicate = (alive, count) -> {
            if (alive) return survivalPredicate.test(count);
            else return birthPredicate.test(count);
        };
    }


    /**
     * Initializes the predicate for when the cell reached the edge
     */
    protected static void initializeEdgeCondition() {

        Predicate<Point3D> pred = (p) -> p.getX() == 0 || p.getX() == matrixSide - 1 || p.getY() == 0 || p.getY() == matrixSide - 1;
        if (dimensions == 3) pred = pred.or((p) -> p.getZ() == 0 || p.getZ() == matrixSide - 1);
        edgePredicate = pred;
    }


    /**
     * Initializes the list of neighbours given the moore depth (default is 1)
     */
    protected static void initializeMooreNeighbours() {

        final Properties properties = System.getProperties();

        // read the moore level, default 1
        int mooreDepth = 1;
        try {
            mooreDepth = Integer.parseInt(properties.getProperty("moore", DEFAULT_MOORE));
            if (mooreDepth <= 0) { printAndExit("Bad moore depth"); }
        } catch (NumberFormatException e) { printAndExit(e.getMessage()); }

        // index for 3D may vary
        final int zIndex = (dimensions == 3) ? mooreDepth : 0;
        mooreNeighbours = new ArrayList<>();

        // initialize with directives
        for (int z = -zIndex; z <= zIndex; z++)
            for (int y = -mooreDepth; y <= mooreDepth; y++)
                for (int x = -mooreDepth; x <= mooreDepth ; x++)
                    mooreNeighbours.add(new Point3D(x, y, z));

        mooreNeighbours.remove(new Point3D(0 ,0, 0));
    }


    /**
     * Creates from a tokenized array the predicate
     * @param array The tokenized array with the form: compare operator - number - binary operator - compare operator - number ...
     * @return The functional predicate
     */
    protected static Predicate<Integer> generatePredicate(String[] array) {
        // for the fist, is mandatory to have minimum a simple predicate
        int i = 0;
        Predicate<Integer> predicate = generateSimplePredicate(array, i);
        i += 2;

        // iterate over all array and append predicates
        while (i < array.length) {
            predicate = generateComplexPredicate(array, i, predicate);
            i += 3;
        }

        return predicate;
    }


    /**
     * Generates a simple predicate, meaning a compare
     * @param array The array from which to obtain the operator and number
     * @param i The index from which to check the array
     * @return The predicate
     */
    protected static Predicate<Integer> generateSimplePredicate(String[] array, int i) {
        // check for index out of range
        if (i + 1 >= array.length) printAndExit("Invalid formatted rule 1");

        // generate corresponding predicate
        try {
            final int num = Integer.parseInt(array[i + 1]);
            switch (array[i]) {
                case ">": return (var) -> var > num;
                case "<": return (var) -> var < num;
                case "=": return (var) -> var == num;
                default: printAndExit("Invalid formatted rule 2");
            }
        } catch (NumberFormatException e) { printAndExit(e.getMessage()); }

        return (c) -> false;
    }


    /**
     * Generates a complex predicate, meaning an or or and of predicates
     * @param array The array from which to obtain the operator
     * @param i The index from which to check the array
     * @param predicate The previous existing predicate to operate over
     * @return The predicate
     */
    protected static Predicate<Integer> generateComplexPredicate(String[] array, int i, Predicate<Integer> predicate) {

        switch (array[i]) {
            case "&": return predicate.and(generateSimplePredicate(array, i + 1));
            case "|": return predicate.or(generateSimplePredicate(array, i + 1));
            default: printAndExit("Invalid formatted rule 3");
        }

        return (c) -> false;
    }

    /**
     * Initializes de matrix given the params taken
     * @param matrixSide The whole matrix side value
     * @param dimensions How many dimensions has the matrix
     * @param initialMatrixSide The initial matrix side value. Should be less than @param matrixSide
     * @param initialOccupationPercentage The initial occupation percentage for the initial matrix
     * @param randomSeed Random seed for shuffling
     * @return The HashSet with the values
     */
    protected static HashSet<Point3D> initializeMatrixRandom(final int matrixSide, final int dimensions, final int initialMatrixSide, final int initialOccupationPercentage, final long randomSeed) {

        // check for invalid relation values
        if (dimensions > 3 || dimensions < 2) printAndExit("Invalid matrix dimension");
        if (matrixSide > 1000 || matrixSide < 1) printAndExit("Invalid matrix side values [0 - 1000]");
        if ((matrixSide - initialMatrixSide) % 2 != 0 || matrixSide < initialMatrixSide) printAndExit("Invalid initial matrix size");
        if (initialOccupationPercentage <= 0 || initialOccupationPercentage > 100) printAndExit("Invalid initial occupation percentage");

        // auxiliary variables for posterior use
        final int initialMaxElements = (int) Math.pow(initialMatrixSide, dimensions);
        final List<Point3D> init = new ArrayList<>(initialMaxElements);

        final int offsetStart = (matrixSide - initialMatrixSide) / 2;
        final int offsetEnd = offsetStart + initialMatrixSide;

        final int zOffsetStart = (dimensions == 3) ? offsetStart : 0;
        final int zOffsetEnd = (dimensions == 3) ? offsetEnd : 1;

        // create all possible valid cells points for initialization
        for (int z = zOffsetStart; z < zOffsetEnd; z++)
            for (int y = offsetStart; y < offsetEnd; y++)
                for (int x = offsetStart; x < offsetEnd; x++)
                    init.add(new Point3D(x, y, z));

        // shuffle the list of all possible cells for initialization
        Collections.shuffle(init, new Random(randomSeed));
        // create hash set with the first given percentage of the possible cells for initialization
        return new HashSet<>(init.subList(0, (initialOccupationPercentage * initialMaxElements) / 100));
    }


    /**
     * Read from the file the general size of the matrix and dimension
     * @param filename The filename to read
     */
    protected static void initializeMatrixVarsFromFile(final String filename) {

        try(BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            dimensions = Integer.parseInt(reader.readLine());
            if (dimensions > 3 || dimensions < 2) printAndExit("Invalid matrix dimension");

            matrixSide = Integer.parseInt(reader.readLine());
            if (matrixSide > 1000 || matrixSide < 1) printAndExit("Invalid matrix side values [0 - 1000]");

        } catch (IOException e) { printAndExit(e.getMessage()); }
    }


    /**
     * Initializes the alive cells from a given file
     * @param filename The filename to read from
     * @return The new HashSet of alive cells
     */
    protected static HashSet<Point3D> initializeMatrixFromFile(final String filename) {

        try(BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            reader.readLine(); // skip first line - 2 or 3D
            reader.readLine(); // skip second line - matrix size
            reader.readLine(); // skip third line - *

            int size = Integer.parseInt(reader.readLine()); // amount of living cells
            final List<Point3D> init = new ArrayList<>(size); // auxiliary array
            final int offset = (center) ? (matrixSide - 1) / 2 : 0;

            for (int i = 0; i < size; i++) {
                String line = reader.readLine();
                if (line == null) throw new IOException();
                Point3D p = new Point3D(line.split(" "), dimensions, offset);
                init.add(p);
            }

            // check if its the final line
            if (reader.readLine() != null) printAndExit("Bad formatted input file");

            return new HashSet<>(init);

        } catch (IndexOutOfBoundsException | IOException | NumberFormatException e) { printAndExit(e.getMessage()); }

        return null;
    }


    /**
     * Prints the cells alive
     * @param set The set with the alive cells
     * @param outFileName The filename prefix
     */
    protected static void printAliveCells(final HashSet<Point3D> set, final String outFileName) {
        try(BufferedWriter writer = new BufferedWriter(new FileWriter(outFileName, true))) {
            writer.write("*\n" + set.size() + "\n");

            final int offset = (center) ? -(matrixSide - 1) / 2 : 0;

            // write each point
            if (dimensions == 3) for (Point3D p : set) writer.write(p.toString3D(offset) + "\n");
            else for (Point3D p : set) writer.write(p.toString2D(offset) + "\n");
        } catch (IOException e) { printAndExit(e.getMessage()); }
    }


    /**
     * Counts the amount of neighbour alive cells
     * @param aliveCells The set of alive cells
     * @param me The position of me
     * @return The amount of alive neighbour cells
     */
    protected static int getAliveNeighbours(final Set<Point3D> aliveCells, final Point3D me) {
        int count = 0;
        for (Point3D neighbour: mooreNeighbours)
            if (aliveCells.contains(neighbour.add(me))) count++;
        return count;
    }

    protected static void printAndExit(String message) {
        System.err.println(message);
        System.exit(ERROR_STATUS);
    }
}
