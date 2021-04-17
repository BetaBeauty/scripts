#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <unordered_map>
#include <set>
#include <unordered_set>
#include <list>
#include <deque>

#include <bbcode/serializer/types.h>

using namespace bbcode;

template<typename T, typename U>
class A {

};

int main() {
  std::cout << TYPE_STR(int) << std::endl;
  std::cout << TYPE_STR(double) << std::endl;
  std::cout << TYPE_STR(float) << std::endl;
  std::cout << TYPE_STR(bool) << std::endl;

  std::cout << "******** array *******" << std::endl;
  std::cout << TYPE_STR(std::vector<int>) << std::endl;
  // unsupported type
  // std::cout << TYPE_STR(int[]) << std::endl;
  // std::cout << TYPE_STR(int[30]) << std::endl;
  std::cout << TYPE_STR(std::map<int, std::string>) << std::endl;
  std::cout << TYPE_STR(std::multimap<int, std::string>) << std::endl;
  std::cout << TYPE_STR(std::unordered_map<int, std::string>) << std::endl;
  std::cout << TYPE_STR(std::unordered_multimap<int, std::string>) << std::endl;

  std::cout << TYPE_STR(std::set<int>) << std::endl;
  std::cout << TYPE_STR(std::multiset<int>) << std::endl;
  std::cout << TYPE_STR(std::unordered_set<int>) << std::endl;
  std::cout << TYPE_STR(std::unordered_multiset<int>) << std::endl;

  std::cout << TYPE_STR(std::list<std::string>) << std::endl;
  std::cout << TYPE_STR(std::deque<int>) << std::endl;

  std::cout << "******** pair *******" << std::endl;
  std::cout << TYPE_STR(std::pair<int, bool>) << std::endl;

  std::cout << "******** string *******" << std::endl;
  std::cout << TYPE_STR(std::basic_string<char>) << std::endl;
  std::cout << TYPE_STR(std::string) << std::endl;
  std::cout << TYPE_STR(const std::string&) << std::endl;
  std::cout << TYPE_STR(const char*) << std::endl;
  std::cout << TYPE_STR(char*) << std::endl;

  std::cout << "******** pointer ********" << std::endl;
  std::cout << TYPE_STR(int*) << std::endl;
  std::cout << TYPE_STR(std::shared_ptr<int>) << std::endl;
  std::cout << TYPE_STR(std::unique_ptr<int>) << std::endl;
  std::cout << TYPE_STR(std::nullptr_t) << std::endl;

  std::cout << "******** custom class ********" << std::endl;
  std::cout << TYPE_STR(A<int, bool>) << std::endl;
}

