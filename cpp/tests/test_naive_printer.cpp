#include <iostream>
#include <set>
#include <deque>

#include <bbcode/ioutils/naive_printer.h>

int main() {
  int i1 = -3, i2 = 27, i3 = 999, i4 = -39, i5 = i1;
  std::vector<int> a{i1, i2, i3, i4};
  bbcode::naive_println(a);

  std::set<int> set1{i1, i3, i4, i5};
  bbcode::naive_println(set1);

  std::deque<int> deque1{i1, i2, i3, i4, i5};
  bbcode::naive_println(deque1);

  std::string s1 = "hello";
  auto b = std::make_pair(s1, a);
  bbcode::naive_println(b);

  const char* s2 = "world";
  std::vector<const char*> c{s2, s1.c_str()};
  bbcode::naive_println(std::make_pair(s2, c));

  int arr1[]{i3, i1, i5};
  bbcode::naive_println(arr1, 3);

  // bbcode::naive_println(s1, "check_end");
  bbcode::naive_println(nullptr);

  return 0;
}
