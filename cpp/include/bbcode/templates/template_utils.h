#ifndef BBCODE_TEMPLATE_UTILS_H
#define BBCODE_TEMPLATE_UTILS_H

namespace bbcode {

namespace details {
typedef char Type1[1];
typedef char Type2[2];
}

template<typename T1, typename T2>
class ConvertFromTo {
  static details::Type1& compatiable( T2 );
  static details::Type2& compatiable( ... );
  static T1 MakeT();
 public:
  enum { value = sizeof(compatiable(MakeT())) == sizeof(details::Type1) };
};

#define HAS_NESTED_TYPE(type) \
  template<typename T> \
  class has_ ## type { \
    template<typename C> \
    static details::Type1& test(typename C::type *); \
    template<typename C> \
    static details::Type2& test( ... ); \
   public: \
    enum { value = sizeof(test<T>(nullptr)) == sizeof(details::Type1) }; \
  };

#define HAS_MEMBER(name) \
  template<typename T> \
  class has_member_ ## name { \
    template<typename U> \
    static details::Type1& test(decltype(&U::name)); \
    template<typename U> \
    static details::Type2& test(...); \
   public: \
    static const bool value = \
      sizeof(test<T>(nullptr)) == sizeof(details::Type1); \
  };

#define HAS_TYPE_MEMBER(name, type) \
  template<typename T> \
  class has_type_member_ ## name { \
    template<typename U> \
    static details::Type1& test( \
      decltype( static_cast<type*>(&U::name) )); \
    template<typename U> static details::Type2& test(...); \
   public: \
    static const bool value = \
      sizeof(test<T>(nullptr)) == sizeof(details::Type1); \
  };


/**
 * Template meta-programming controllers.
 **/
template<bool, typename Then, typename Else>
class T_IF {};

template<typename Then, typename Else>
class T_IF<true, Then, Else> { public: typedef Then reType; };
template<typename Then, typename Else>
class T_IF<false, Then, Else> { public: typedef Else reType; };

template<template<typename> class Condition, typename Statement>
class T_WHILE {
  template<typename> class Stop { public: typedef Statement reType; };
 public:
  typedef typename T_IF<
    Condition<Statement>::ret,
    T_WHILE<Condition, typename Statement::Next>,
    Stop<Statement>>::reType::reType 
  reType;
};

template<typename T>
void null_deleter(T*) {}

} // namespace bbcode

#endif // BBCODE_TEMPLATE_UTILS_H
