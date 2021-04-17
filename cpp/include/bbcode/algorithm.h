#ifndef CODE_ALGORITHM_H
#define CODE_ALGORITHM_H

#include <algorithm>

namespace bbcode {

template<typename Type>
inline Type max(std::initializer_list<Type> const& args) {
  Type res = std::numeric_limits<Type>::min();
  for (Type const& arg : args) res = std::max(res, arg);
  return res;
}

template<typename Type>
inline Type max(Type const& t1, Type const& t2) {
  return std::max(t1, t2);
}

}

#endif // CODE_ALGORITHM_H
