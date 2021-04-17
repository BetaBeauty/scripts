#include <bbcode/common_header.h>
#include <bbcode/ioutils/naive_printer.h>

template<typename T, int VAL>
T addValue(T const& x) {
  return x + VAL;
}

using namespace std;

int main() {
  vector<int> src{ 1, 2, 3, 4, 5 };
  std::transform(src.begin(), src.end(), src.begin(), 
      [](int const &x) {
        return x + 3;
      });

  bbcode::naive_print(src);

  std::transform(src.begin(), src.end(), src.begin(), 
      addValue<int, 3>);
  
  bbcode::naive_print(src);
  return 0;
}
