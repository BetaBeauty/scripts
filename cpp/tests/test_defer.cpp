#include <iostream>

#include <bbcode/utils/defer.h>

using namespace bbcode;

int main() {
  AUTO_DEFER() {
    std::cout << "defer function without parameter." << std::endl;
  };

  DEFER_FUNC(ddd) {
    std::cout << "defer function with parameter." << std::endl;
  };

  ddd.cancel();

  std::cout << "should run after this" << std::endl;

  return 0;
}
