#ifndef BBCODE_TYPES_H
#define BBCODE_TYPES_H

#include <memory>

#include <bbcode/templates/stl_container.h>
#include <bbcode/errors.h>

namespace bbcode {

// TODO: pod type support, could copy via `memcpy` function.
enum FormatType {
  // unknown type, like user-defined class and some unfrequent
  // useful stl class
  UNKNOWN,
  /**
   * std::is_arthimetic,
   * including integral types and floating point types.
   *
   * integral types: <std::is_integral>
   * ---------------
   * bool,
   * char, char16_t, char32_t,
   * wchar_t,
   * signed char, unsigned char
   * short_int, int, long int, long long int,
   * unsigned short int, unsigned int, unsigned long int,
   * unsigned long long int
   *
   *
   * floating point types: <std::is_floating_point>
   * ---------------------
   * float,
   * double, long double
   */
  ARITHMETIC,
  // naive string type, including std::string, [const] char *
  STRING,
  // TODO: add pod type as basic type
  /**
   * stl container compatiable types,
   * including map, set, vector, list, deque and some
   * user-defined well-interface class(aka has begin,
   * end, const iterator, ... etc member functions)
   *
   * more details reference to examine method:
   *  bbcode::is_stl_container_compatiable_type
   *
   * usages like:
   *  for (auto &&it = data.begin(); it != data.end(); ++it)
   */
  ARRAY,
  // pair type, supports memeber access with `.first` and `.second`
  PAIR,
  // contrains nullptr, shared pointer & unique pointer
  POINTER, 
  // user-defined class
  CLASS,
  // user-defined enumerate type
  ENUMERATE,
};

std::string type2str(int type) {
  std::string s;
  switch (type) {
    case FormatType::UNKNOWN: { s = "unknown type"; break; }
    case FormatType::ARITHMETIC: { s = "arithmetic type"; break; }
    // case FormatType::BOOL: { s = "bool type"; break; }
    case FormatType::ARRAY: { s = "iterable array type"; break; }
    case FormatType::PAIR: {s = "pair type"; break; }
    case FormatType::STRING: { s = "string type"; break; }
    case FormatType::POINTER: { s = "pointer type"; break; }
    default: {
      CHECK(false) << "unknown error type: " << type;
    }
  }
  return s;
}

// default base type
template<
  typename T,
  // extra template parameters:U to indicate stl constainer type
  typename U = void
>
class TypeInfo { public: enum { value = FormatType::UNKNOWN }; };

// arithmetic type
template<typename T>
class TypeInfo<T, typename std::enable_if<
    std::is_arithmetic<T>::value>::type> {
  public: enum { value = FormatType::ARITHMETIC };
};

// string compatiable type
template<>
class TypeInfo<std::string> { public: enum { value = FormatType::STRING }; };

template<>
class TypeInfo<char*> { public: enum { value = FormatType::STRING }; };

template<>
class TypeInfo<const char*> { public: enum { value = FormatType::STRING }; };

// std container array type
template<typename T>
class TypeInfo<T,
    typename std::enable_if<
      is_stl_container_compatiable_type<T>::value>::type> {
  public: enum { value = FormatType::ARRAY };
};

// c++ naive array type
// template<typename T>
// class TypeInfo<T[]> { public: enum { value = FormatType::ARRAY }; };
// template<typename T, int N>
// class TypeInfo<T[N]> { public: enum { value = FormatType::ARRAY }; };


// std pair type
template<typename T1, typename T2>
class TypeInfo<std::pair<T1, T2>> {
  public: enum { value = FormatType::PAIR };
};

// c++ naive pointer type
template<typename T>
class TypeInfo<T*> { public : enum { value = FormatType::POINTER }; };

// c++ wrappered pointer type
template<typename T>
class TypeInfo<std::shared_ptr<T>> { 
  public: enum { value = FormatType::POINTER }; 
};
template<typename T>
class TypeInfo<std::unique_ptr<T>> { 
  public: enum { value = FormatType::POINTER }; 
};

// c++ null pointer type
template<>
class TypeInfo<std::nullptr_t> {
  public: enum { value = FormatType::POINTER };
};

#define TYPE_VALUE(...) \
  TypeInfo< \
    typename std::remove_cv< \
      typename std::remove_reference<__VA_ARGS__>::type \
    >::type> \
  ::value

#define TYPE_STR(...) \
  type2str(TYPE_VALUE(__VA_ARGS__))

} // namespace bbcode

#endif // BBCODE_TYPES_H
