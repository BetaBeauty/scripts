#include <bbcode/ioutils/ioutils.h>
#include <bbcode/ioutils/leetcode.h>
#include <bbcode/common_header.h>
#include <bbcode/ioutils/naive_printer.h>

int main() {
  std::set<int> a { 1, 2, 3, 4, 6, 7 };

  bbcode::Writer<bbcode::NaiveFormater>()
    .write(a, bbcode::VectorWriteOption{{0, "[", "]\n"}, ", "});

  std::vector<std::vector<int>> b {
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9}
  };

  bbcode::set_global_ident(" ");
  // code::Writer<code::LeetCodeFormater>().write(b, false, false);
  bbcode::Writer<bbcode::NaiveFormater>().write(
      &b,
      // std::make_shared<std::vector<std::vector<int>>>(b),
      bbcode::VectorWriteOption{{0, "[\n", "\n]\n"}, ",\n"},
      bbcode::VectorWriteOption{{1, "[", "]"}, ", "});
  bbcode::Writer<bbcode::NaiveFormater>().write(nullptr);
  bbcode::Writer<bbcode::NaiveFormater>().write(true);
  // code::print(nullptr);
  
  bbcode::Writer<bbcode::LeetCodeFormater>().write(&b, false);
  bbcode::naive_print(nullptr);
  return 0;
}
