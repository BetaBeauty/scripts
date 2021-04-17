#ifndef BBCODE_CALGO_H
#define BBCODE_CALGO_H

#include <cmath>

namespace bbcode {

// GCD, LCM
int gcd(int a, int b) { return b ? gcd(b, a % b) : a ; }
int lcm(int a, int b) { return a * b / gcd(a, b); }

// number length for n! 
int length_for_n(int n) {
  double len = 0;
  for (int i = 2; i <= n; ++i) len += std::log10(i * 1.0);
  return (int)len + 1;
}

// 斯特林公式
int length_for_n2(int n) {
  double len = 0.2 * std::log10(2 * 3.1415927 * n) +
    n * std::log10(n / 2.718281828459);
  return (int)len + 1;
}

// quick power calculation, a ^ n % mod
long long pow(long long a, long long n) {
  long long ret = 1;
  while (n) {
    if (n & 1) ret *= a;;
    a *= a;
    n >>= 1;
  }
  return ret;
}

long long mod_pow(long long a, long long n, long long mod) {
  long long ret = 1;
  while (n) {
    if (n & 1) ret = (ret * a) % mod;
    a = (a * a) % mod;
    n >>= 1;
  }
  return ret;
}

// 求1到n的数的异或和O（1）
unsigned xor_n(unsigned n) {
  unsigned t = n & 3;
  if (t & 1) return t / 2u ^ 1;
  return t / 2u ^ n;
}

}

#endif // BBCODE_CALGO_H
