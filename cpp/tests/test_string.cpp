
#include <cstdio>
#include <cstring>
#include <vector>
#include <algorithm>

#include <bbcode/ioutils/naive_printer.h>
#include <bbcode/dsa/string_helper.h>

int main() {
  std::string pat = "BBBD";
  std::vector<int> next(pat.size());

  bbcode::kmp_next_build(
      const_cast<char*>(pat.c_str()),
      pat.size(), next.data());

  std::vector<int> next2(pat.size());
  bbcode::kmp_get_next(
      const_cast<char*>(pat.c_str()),
      pat.size(), next2.data());

  std::cout << pat << std::endl;
  bbcode::naive_print(next, "\n", " ");
  bbcode::naive_print(next2, "\n", " ");

  std::string text = "DKBBDLSBBBDDBDBBBBDDIE";
  int index = bbcode::kmp_match(text, pat);
  std::cout << "Match index: " << index
    << " out of size " << text.size() << std::endl;

  std::sort(next.begin(), next.end());

  return 0;
}
