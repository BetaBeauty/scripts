# README

## Connection

Run those commands in local machines to connect with CortexLabs community:

1. git clone git@github.com:ntop/n2n.git

2. git co 84ec5c6

3. mkdir build

4. cd build && cmake .. && make -j8

5. build/edge -c Cortex_Labs_Foundation -k Guess_What_Password_For_Cortex -l 101.200.44.74:7654 -f -v

## Manager

You could lookup available services with command, press Enter manually:

netcat -u localhost -p 5644
