all: _hook.so

wrapper.c: hook.i
	swig -python -o wrapper.c hook.i

wrapper.o: wrapper.c
	gcc -I/usr/include/python2.7 -fPIC -c wrapper.c

hook.o: hook.c
	gcc -fPIC -c hook.c

_hook.so: hook.o wrapper.o
	gcc -shared wrapper.o hook.o -lpython2.7 -o _hook.so

clean:
	rm -f wrapper.c wrapper.o hook.o hook.so _hook.so hook.py hook.pyc
