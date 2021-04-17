#ifndef DSA_H
#define DSA_H

#include "./ioutils.h"

namespace bbcode {

template<typename T>
class DSAReader : public ReadHelper<T> {
 public:
  DSAReader(std::istream & is)
    : ReadHelper<T>(is, _default_read_option) {}
};

}

#endif // DSA_H
