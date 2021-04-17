#ifndef BBCODE_SORT_H
#define BBCODE_SORT_H

namespace bbcode {

/*!
 * Template Based Sort Functions
 *
 * User can override the operator <, <= to achieve custom
 *  definition over sort criterion.
 */

template<typename T>
void bubble_sort(T *D, int low, int high) {
  for (int i = 0; i < high; ++i) {
    for (int j = i+1; j < high; ++j) {
      if (D[j] < D[i]) { // comparasion judgement
        swap(D, i, j);
      }
    }
  }
}

template<typename T>
void quick_sort(T *D, int low, int high) {
  if (low + 1 >= high) return ;

  // if (low + 10 > high) return bubble_sort(D, low, high);

  // swap(D, low, (low+high)/2);
  int i = low, j = high-1;
  T tmp = D[i];
  while (i < j) {
    while (i < j && tmp <= D[j]) j--;
    D[i] = D[j];
    while (i < j && D[i] <= tmp) i++;
    D[j] = D[i];
  }
  D[i] = tmp;

  quick_sort(D, low, i);
  quick_sort(D, i+1, high);
}

template<typename T>
void merge_sort(T *D, int low, int high) {
  if (low + 1 >= high) return ;

  int mid = (low + high) / 2;
  merge_sort(D, low, mid);
  merge_sort(D, mid, high);
  
  T* M = new T[mid - low];

  int i = 0, s = mid - low, j = mid, t = low;
  memcpy(M, D + low, s * sizeof(T));
  while (i < s && j < high) {
    if (M[i] < D[j]) D[t++] = M[i++];
    else D[t++] = D[j++];
  }

  if (i < s)
    memcpy(D + t, M + i, (s - i) * sizeof(T));

  delete[] M;
}

}

#endif // BBCODE_SORT_H
