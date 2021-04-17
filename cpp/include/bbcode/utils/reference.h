#ifndef BBCODE_REFERENCE_H
#define BBCODE_REFERENCE_H

#include <cstdio>
#include <algorithm>

namespace bbcode {

// array sort
template<typename T>
void swap(T *a, T *b) {
 T tmp = (*a);
 (*a) = (*b);
 (*b) = tmp;
}

void swap(int *D, int i, int j) {
  int tmp = D[i];
  D[i] = D[j];
  D[j] = tmp;
}

// text file input and output
#define FRE_IN std::freopen(fpath, "r", stdin);
#define FRE_OUT std::freopen(fpath, "w", stdout);

// array deduplicate
template<typename DType>
int deduplicate(DType *D, int N) {
  std::sort(D, D + N);
  int len = std::unique(D, D + N) - D;
  return len;
}

// int conversion with string
#define STR2INT(s, n) std::sscanf(s, "%d", &n);
#define INT2STR(s, n) std::sprintf(s, "%d", n);

// getchar read and transform into string
void read_stdin() {
  int buffer_size = 1000;
  int x[buffer_size];

  while ((x[0] = std::getchar()) && x[0] != '\n') {
    int len = 1;
    while ((x[len] = getchar()) && x[len] != ' ') len ++;
    x[len] = '\0';
  }
}

// string<const char*> to int
#define CHAR2INT(s) atoi(s);

// input quick reader and output quick putter
template<typename T>
inline void scan_d(T &ret) {
  char c; int sgn;
  while (c != '-' && (c < '0' || c > '9')) c = getchar();
  sgn = (c == '-') ? -1 : 1;
  ret = (c == '-') ? 0 : (c - '0');
  while (c = getchar(), c >= '0' && c <= '9')
    ret = ret * 10 + (c - '0');
  ret *= sgn;
}

template<typename T>
inline void scan_ud(T &ret) {
  char c;
  while (c < '0' || c > '9') c = getchar();
  ret = c - '0';
  while (c = getchar(), '0' <= c && c <= '9') 
    ret = (ret << 1) + (ret << 3) + (c - '0');
}

template<typename T>
inline void print_d(T x) {
  if (x > 9) out (x / 10);
  putchar(x % 10 + '0');
}

}

#endif // BBCODE_REFERENCE_H
