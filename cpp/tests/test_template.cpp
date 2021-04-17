#include <vector>
#include <set>
#include <iostream>

#include <bbcode/templates/template_utils.h>
#include <bbcode/templates/stl_container.h>
#include <bbcode/ioutils/naive_printer.h>

using namespace bbcode;

class object {
 public:
  // typedef int const_iterator;
  class const_iterator { };
  // typedef std::vector<int> const_iterator;
  const_iterator begin() const;
  const_iterator end() const;
};

int main() {
  std::cout << details::has_const_iterator<std::vector<int>>::value << std::endl;
  std::cout << details::has_const_iterator<std::set<int>>::value << std::endl;
  std::cout << details::has_const_iterator<int>::value << std::endl;
  std::cout << details::has_const_iterator<object>::value << std::endl;

  std::cout << "============" << std::endl;

  std::cout << details::has_begin_end<int>::value << std::endl;
  std::cout << details::has_begin_end<std::vector<int>>::value << std::endl;
  std::cout << details::has_begin_end<std::set<int>>::value << std::endl;
  std::cout << details::has_begin_end<object>::value << std::endl;

  std::cout << is_stl_container_compatiable_type<int>::value << std::endl;
  std::cout << is_stl_container_compatiable_type<std::vector<int>>::value << std::endl;
  std::cout << is_stl_container_compatiable_type<std::set<int>>::value << std::endl;
  std::cout << is_stl_container_compatiable_type<object>::value << std::endl;

  std::cout << "////////" << std::endl;

  std::cout << type2str(TypeInfo<int*>::value) << std::endl;
  std::cout << type2str(TypeInfo<int>::value) << std::endl;
  std::cout << type2str(TypeInfo<std::vector<int>>::value) << std::endl;

  std::cout << "ddddddddd" << std::endl;
  std::shared_ptr<int> a;
  naive_print(a);

  std::set<int> s { 1, 3, 4 };
  naive_print(&s);

}
