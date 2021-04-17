#ifndef CODE_TIMES_H
#define CODE_TIMES_H

#include <iostream>
#include <chrono>
#include <iomanip>

namespace bbcode {

#define TIME_START(id) \
  auto _BBTIME_START_ ## id = std::chrono::high_resolution_clock::now();

#define TIME_ELAPSED(id) \
  auto _BBTIME_END_ ## id = std::chrono::high_resolution_clock::now(); \
  double elapsed = std::chrono::duration_cast< \
    std::chrono::microseconds>( \
      _BBTIME_END_ ## id - _BBTIME_START_ ## id).count(); \
  std::cout << "Elapsed time: " << std::setw(10) \
    << elapsed / 1000 << " ms\n";

}

#endif // CODE_TIMES_H
