set breakpoint pending on
break my_dumb_hook
commands
printf "Look, we stopped in the C code!\n"
continue
end
run hook2.py
quit
