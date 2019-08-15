// javac Foo.java && java -ea Foo [1] [2]

interface FooInterface {
    public int add(int x, int y);
}

class FooContract implements FooInterface {
    private FooInterface impl;

    public FooContract(FooInterface _impl) {
        this.impl = _impl;
    }

    public int add(int x, int y) {
        assert (x >= 0 && x <= 1) : "Precondition x: " + Integer.toString(x);
        assert (y >= 0 && y <= 1) : "Precondition y: " + Integer.toString(y);

        int r = this.impl.add(x, y);

        assert r >= 0 : "Postcondition: " + Integer.toString(r);
        assert r <= 2 : "Postcondition: " + Integer.toString(r);

        return r;
    }
}

class FooImpl implements FooInterface {
    private static FooInterface _instance = null;

    public static FooInterface getInstance() {
        if (_instance == null)
            _instance = new FooContract(new FooImpl());
        return _instance;
    }

    public int add(int x, int y) {
        if (Foo.BADNESS1)
            return x + y + 9;
        else
            return x + y;
    }
}

class Foo {
    static boolean BADNESS1 = false;
    static boolean BADNESS2 = false;

    public static void main(String[] args) {
        for (String arg : args) {
            if ("1".equals(arg))
                BADNESS1 = true;
            else if ("2".equals(arg))
                BADNESS2 = true;
        }
        FooInterface f = FooImpl.getInstance();
        if (BADNESS2)
            System.out.println(f.add(5, 8));
        else
            System.out.println(f.add(1, 1));
    }
}
