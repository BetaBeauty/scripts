// 计算 1^e+2^e+...+n^e
#include <iostream>
#include <vector>

#include <bbcode/templates/template_utils.h>
#include <bbcode/templates/stl_container.h>

using namespace bbcode;

template<int i, int j>
class power_i { public: enum { ret = i * power_i<i, j-1>::ret }; };
template<int i>
class power_i<i, 0> { public: enum { ret = 1 }; };

template<int n, int e>
class sum_pow_net {
  template<int i>
  class power { public: enum { ret = power_i<i, e>::ret }; };

  template<typename stat>
  class cond { public: enum { ret = (stat::ri <= n) }; };
  template<int i, int sum = 0>
  class stat { 
   public:
    enum { ri = i, ret = sum };
    typedef stat<i+1, sum + power<i>::ret> Next;
  };
  
 public:
  enum { ret = T_WHILE<cond, stat<1>>::reType::ret };
};

template<int n, int e>
class sum_pow_mod {
  template<int i>
  class power { public: enum { ret = power_i<i, e>::ret }; };

  template<typename stat>
  class cond { public: enum { ret = (stat::ri < n) }; };
  template<int i, typename _T = int>
  class stat { 
   public:
    enum { ri = i, ret = stat<i-1, _T>::ret + power<i>::ret };
    typedef stat<i+1, _T> Next;
  };

  template<typename _T>
  class stat<0, _T> { 
   public: 
    enum { ret = 0 }; 
  };
  
 public:
  enum { ret = T_WHILE<cond, stat<1>>::reType::ret };
};

template<int n, int e>
class sum_pow_wlt {
  template<int i>
  class power { public: enum { ret = power_i<i, e>::ret }; };
 public:
  enum { ret = sum_pow_wlt<n-1, e>::ret + power<n>::ret };
};
template<int e>
class sum_pow_wlt<1, e> {
 public:
  enum{ ret = 1 };
};

int main() {
  std::cout << std::is_same<
    std::vector<int>::iterator::iterator_category,
    std::random_access_iterator_tag>::value << std::endl;

  std::cout << ConvertFromTo<int, double>::value << std::endl;
  std::cout << ConvertFromTo<double, int*>::value << std::endl;
  std::cout << details::has_value_type<std::vector<int>>::value << std::endl;
  std::cout << details::has_value_type<int>::value << std::endl;
  std::cout << std::vector<int>::value_type(5) << std::endl;

  std::cout << sum_pow_net<5, 2>::ret << std::endl;
  std::cout << sum_pow_mod<5, 2>::ret << std::endl;
  std::cout << sum_pow_wlt<5, 2>::ret << std::endl;
  return 0;
}
