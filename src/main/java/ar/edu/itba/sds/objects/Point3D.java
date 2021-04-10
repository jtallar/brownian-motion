package ar.edu.itba.sds.objects;



public class Point3D {

    private int x;
    private int y;
    private int z;

    public Point3D(final int x, final int y, final int z) {
        this.x = x;
        this.y = y;
        this.z = z;
    }

    public Point3D(final int value, final int module) {
        this.x = value % module;
        this.y = ((value - x) / module) % module;
        this.z = ((value - module * y - x) / (module * module)) % module;
    }

    public Point3D(final String[] s, final int dimensions, final int offset) throws NumberFormatException, IndexOutOfBoundsException {
        this.x = Integer.parseInt(s[0]) + offset;
        this.y = Integer.parseInt(s[1]) + offset;
        this.z = (dimensions == 3) ? Integer.parseInt(s[2]) + offset : 0;
        if (this.x < 0 || this.y < 0 || this.z < 0) throw new NumberFormatException("Bad center input file");
    }

    public Point3D add(final Point3D p) {
        return new Point3D(x + p.x, y + p.y, z + p.z);
    }


    public Point3D move(final int dx, final int dy, final int dz) {
        this.x += dx;
        this.y += dy;
        this.z += dz;
        return this;
    }

    public Point3D move(final int dx, final int dy) {
        return move(dx, dy, 0);
    }

    public int getX() {
        return x;
    }

    public int getY() {
        return y;
    }

    public int getZ() {
        return z;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Point3D point3D = (Point3D) o;
        return x == point3D.x && y == point3D.y && z == point3D.z;
    }

    @Override
    public int hashCode() {
        int hash = 1;
        hash = 1009 * hash + getX();
        hash = 1009 * hash + getY();
        return 1009 * hash + getZ();
    }

    @Override
    public String toString() {
        return "Point3D{" +
                "x=" + x +
                ", y=" + y +
                ", z=" + z +
                '}';
    }

    public String toString2D() {
        return x + " " + y;
    }

    public String toString3D() {
        return x + " " + y + " " + z;
    }

    public String toString2D(final int offset) {
        return (x + offset) + " " + (y + offset);
    }

    public String toString3D(final int offset) {
        return (x + offset) + " " + (y + offset) + " " + (z + offset);
    }
}
