#include <iostream>

#include <bbcode/hack/member_access.h>

class base
{
    int x_ = 0;

public:
    int x() { return x_; }
}; // class base

class derived1 : public base
{
    int x_ = 1;

public:
    int x() { return x_; }
}; // class derived1

class derived2 : public base
{
    int x_ = 2;

public:
    int x() { return x_; }
}; // class derived2

HIJACKER(base, x_, int);
HIJACKER(derived1, x_, int);

// namespace bbcode {
// namespace hijack {
// 
// template<class> struct tag_x_;
// 
// inline auto get(tag_x_<base>) -> type_identity_t<int> base::*;
// 
// template<>
// struct tag_x_<base> {
//   tag_x_(tag_x_*) {}
//   template<class T, class=typename std::enable_if<
//     !is_complete<tag_x_<T>>::value && std::is_base_of<base, T>::value>::type>
//   tag_x_(tag_x_<T>*) {}
// };
// 
// template<type_identity_t<int> base::* Ptr>
// struct hijack_x__48 {
//   friend auto get(tag_x_<base>) -> type_identity_t<int> base::* {
//     return Ptr;
//   }
// };
// 
// template struct hijack_x__48<&base::x_>;
// 
// }
// }

int main() {
  derived1 d1;
  derived2 d2;
  base& b1 = d1;
  base& b2 = d2;
  std::cout << "(" << b1.x() << ", " << d1.x() << "), (" << b2.x() << ", " << d2.x() << ")\n";

  // (&b1)->*bbcode::hijack::get(
    // static_cast<std::add_pointer<bbcode::hijack::tag_x_<base>>::type>(nullptr)) = 233;
  // HIJACK(&b1, x_);
  HIJACK(&b1, x_) = HIJACK(&b2, x_) = 233;
  std::cout << "(" << b1.x() << ", " << d1.x() << "), (" << b2.x() << ", " << d2.x() << ")\n";
  HIJACK(&d1, x_) = HIJACK(&d2, x_) = 666;
  std::cout << "(" << b1.x() << ", " << d1.x() << "), (" << b2.x() << ", " << d2.x() << ")" << std::endl;
  return 0;
}
