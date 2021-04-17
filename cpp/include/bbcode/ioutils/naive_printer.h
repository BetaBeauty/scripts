#ifndef BBCODE_NAIVE_PRINTER_H
#define BBCODE_NAIVE_PRINTER_H

#include <iostream>

#include <bbcode/serializer/types.h>
#include <bbcode/errors.h>

namespace bbcode {

// pre-declaration
namespace details {

template<int type>
struct PrintHelper;

// Provided some hack mechanism to reset the output stream.
static std::ostream* _naive_ostream = &std::cout;

} // namespace details

inline void reset_printer_ostream(std::ostream &os) {
  details::_naive_ostream = &os;
}

// Function template partial specialization is not allow,
//  so use the class template helper.
template<typename T, typename ...Args>
void naive_print(T data, Args && ...args) {
  details::PrintHelper<TYPE_VALUE(T)>(data, args...);
}

template<typename T, typename ...Args>
void naive_print(T *data, int size, Args && ...args) {
  std::vector<T> d(data, data + size);
  naive_print(d, args...);
}

template<typename T, typename ...Args>
void naive_println(T data, Args && ...args) {
  naive_print(data, "\n", args...);
}

template<typename T, typename ...Args>
void naive_println(T *data, int size, Args && ...args) {
  naive_print(data, size, "\n", args...);
}

// details implementation
namespace details {

template<int type> // unknown type
struct PrintHelper {
  template<typename ...Args>
  PrintHelper(Args && ...args) {
    CHECK(false) << "unknown type for printer";
  }
};

template<>
struct PrintHelper<FormatType::ARITHMETIC> {
  template<typename T, typename ...Args>
  PrintHelper(T const& data, 
              std::string const& end = "",
              Args && ...args) {
    CHECK(sizeof...(args) == 0)
      << "base type `" << data
      << "` should with an single end parameter";
    (*details::_naive_ostream) << data << end;
  }

  // TODO: bool serializer inter-medianware
  template<typename ...Args>
  PrintHelper(bool const& data, 
              std::string const& end = "",
              Args && ...args) {
    CHECK(sizeof...(args) == 0)
      << "bool type `" << data
      << "` should with an single end parameter";
    (*details::_naive_ostream) << (data ? "true" : "false") << end;
  }

};

template<>
struct PrintHelper<FormatType::ARRAY> {
  template<typename T, typename ...Args>
  PrintHelper(T const& data,
              std::string const& end = "",
              std::string const& inter_end = ",",
              Args && ...args) {
    (*details::_naive_ostream) << "[";
    for (auto &&it = data.begin(); it != data.end(); ++it) {
      if (it != data.begin())
        (*details::_naive_ostream) << inter_end;
      naive_print(*it, args...);
    }
    (*details::_naive_ostream) << "]" << end;
  }
};

template<>
struct PrintHelper<FormatType::PAIR> {
  template<typename T, typename ...Args>
  PrintHelper(T const& data,
              std::string const& end = "",
              Args && ...args) {
    std::cout << "(";
    naive_print(data.first);
    std::cout << ",";
    naive_print(data.second, args...);
    std::cout << ")" << end;
  }
};

template<>
struct PrintHelper<FormatType::STRING> {
  template<typename T, typename ...Args>
  PrintHelper(T const& data,
              std::string const& end = "",
              Args && ...args) {
    CHECK(sizeof...(args) == 0)
      << "string type `" << data
      << "` should with an single end parameter";
    (*details::_naive_ostream) << data << end;
  }
};

template<>
struct PrintHelper<FormatType::POINTER> {
  template<typename T, typename ...Args>
  PrintHelper(T const& data,
              std::string const& end = "",
              Args && ...args) {
    naive_print(*data, args...);
  }

  template<typename ...Args>
  PrintHelper(std::nullptr_t, std::string const& end = "",
              Args && ...args) {
    CHECK(sizeof...(args) == 0)
      << "nullptr should with an single end parameter";
    (*details::_naive_ostream) << "null pointer" << end;
  }
};

} // namespace details

} // namespace bbcode

#endif // BBCODE_NAIVE_PRINTER_H
