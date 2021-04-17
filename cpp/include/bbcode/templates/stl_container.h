#ifndef CODE_STL_CONTAINER_H
#define CODE_STL_CONTAINER_H

#include <type_traits>

#include "./template_utils.h"

namespace bbcode {

namespace details {

HAS_NESTED_TYPE(value_type);
HAS_NESTED_TYPE(const_iterator);

template<typename T>
class has_begin_end {
  template<typename C>
  static Type1& f(decltype(
    static_cast<typename C::const_iterator (C::*)() const>(&C::begin)));
  // template<typename C>
  // static Type1& f(typename std::enable_if<
  //   std::is_same<decltype(static_cast<
  //     typename C::const_iterator (C::*)() const>(&C::begin)),
  //   typename C::const_iterator(C::*)() const>::value, void>::type*);

  template<typename C>
  static Type2& f( ... );

  template<typename C>
  static Type1& g(decltype(
    static_cast<typename C::const_iterator (C::*)() const>(&C::end)));
  // template<typename C>
  // static Type1& g(typename std::enable_if<
  //   std::is_same<decltype(static_cast<
  //     typename C::const_iterator (C::*)() const>(&C::end)),
  //   typename C::const_iterator(C::*)() const>::value, void>::type*);

  template<typename C>
  static Type2& g( ... );

 public:
  enum { 
    value = (sizeof(f<T>(nullptr)) == sizeof(Type1) &&
             sizeof(g<T>(nullptr)) == sizeof(Type1))
  };

};

} // namespace details

template<typename T>
class is_stl_container_compatiable_type : 
  public std::integral_constant<bool, 
    details::has_value_type<T>::value &&
    details::has_const_iterator<T>::value && 
    details::has_begin_end<T>::value>
{};

}

#endif // CODE_STL_CONTAINER_H
