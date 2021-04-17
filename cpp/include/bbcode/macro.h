#ifndef CODE_MACRO_H
#define CODE_MACRO_H

#define CODE_CORE

#define T_LT(a, b) (a < b)
#define T_EQ(a, b) (a == b)

#ifndef __CONCAT
#define __CONCAT(a, b) a ## b
#endif
#define CONCAT(a, b) __CONCAT(a, b)

/**
 * Notice: the ARGS_COUNT macro cannot count the empty
 *  parameters input. That is the result will be one even
 *  if you invoke this macro like `ARGS_COUNT()`.
 **/
#define ARGS_COUNT_( \
    _0, _1, _2, _3, _4, _5, _6, _7, _8, _9, \
    _10, _11, _12, _13, _14, _15, _16, N, ...) N
#define ARGS_COUNT(args...) ARGS_COUNT_( 0, ##args, \
    16, 15, 14, 13, 12, 11, 10, \
    9, 8, 7, 6, 5, 4, 3, 2, 1, 0)

#define DEFAULT_ARG(arg, def_val) (#arg[0]) ? (arg + 0) : def_val

#endif // CODE_MACRO_H
