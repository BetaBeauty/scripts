#ifndef CODE_STRING_H
#define CODE_STRING_H

#include <cstring>
#include <functional>

// #include <bbcode/ioutils/naive_printer.h>

namespace bbcode {


// Maximum Prefix Substring Match, O(n)
void maximum_prefix_match(char *str, int size, int *ss) {
  // the start location matches all string by default,
  //  generally it will require the starting scanning
  //  at the next for loop throughing into the Else branch.
  ss[0] = size; 

  // We maintain a preview compared range: [lo, hi),
  //  whereas j is the current index to find.
  for (int lo = 0, hi = lo, j = lo+1; j < size; ++j) {
    /**
     * If j < hi, it means the last comparasion matches
     *  a lot, and it's across the furture index viewed
     *  from last check index.
     *
     * And then we continue to compare the existed result
     *  from ss, whose coresponding match index is the
     *  number count from lo to j.
     *
     * If the cached match result is less than the left
     *  match number, just assign to the newer one.
     *
     * **Notice** the last condition mustn't be equal,
     *  since we still have the responsibility to scan
     *  for next characters, which means that jump into
     *  the Else branch codes.
     **/
    if ((j < hi) && (ss[j - lo] < hi - j))
      ss[j] = ss[j - lo]; // assignment
    /**
     * Else branch have two situations:
     *
     * - the j is out of range [lo, hi), and we need to
     *   reset the lo and hi as j to start scanning again.
     *
     * - the j is in range [lo, hi), but ss[j - lo] reaches
     *   the maximum value. Luckily, we still have the
     *   confidence to affirm the data in range [j, hi)
     *   have been compared and be exactly matched. So the
     *   following task is still to compared the next
     *   characters starting from hi until the string end.
     *
     * To sum up, the two situations analysed above are the
     *  same process logic represented as the following
     *  source codes.
     **/
    else {
      lo = j; // set the match lower bound as current index
      if (hi < lo) hi = lo; // situation one's pre-process
      while ((hi < size) && (str[hi] == str[hi-lo]))
        ++hi; // main process logic
      ss[j] = hi - lo; // get the result
    }
  }
}

// Maximum Suffix Substring Match, O(n)
//  The function is symmetric with function:
//  maximum_prefix_match, just check the above function
//  with exhaustive comments.
void maximum_suffix_match(char *str, int size, int *ss) {
  ss[size-1] = size;

  for (int lo = size-1, hi = lo, j = lo-1; j >= 0; --j) {
    if ((lo < j) && (ss[(size-1)-(hi-j)] < j - lo))
      ss[j] = ss[(size-1)-(hi-j)];
    else {
      hi = j;
      if (hi < lo) lo = hi;
      while ((0 <= lo) &&
             (str[lo] == str[(size-1)-(hi-lo)]))
        lo--;
      ss[j] = hi - lo;
    }
  }

}

// ============ KMP ==================
void kmp_next_build(char *pat, int size, int *next) {
  maximum_prefix_match(pat, size, next);

  // puts("maximum prefix match: ");
  // naive_print(next, size, "\n", " ");

  for (int i = size-1; i >= 0; --i) {
    int real_index = i + next[i];
    if (real_index < size)
      next[real_index] = next[i];
    next[i] = pat[0] == pat[i] ? -1 : 0;
  }
}

void kmp_get_next(char *pat, int size, int *next) {
  next[0] = -1;
  int i = 0, j = -1;

  while (i < size-1) {
    if (j == -1 || pat[i] == pat[j]) {
      ++i; ++j;
      // next[i] = j;
      next[i] = pat[i] == pat[j] ? next[j] : j;
    } else {
      j = next[j];
    }
  } 
}

int kmp_match(char *text, int tsize,
              char *pat, int psize,
              int *next) {
  int i = 0, j = 0;

  while (i < tsize && j < psize) {
    if (j == -1 || text[i] == pat[j]) {
      i++; j++;
    } else {
      j = next[j];
    }
  }
  return i - j;
}

int kmp_match(std::string const& text,
              std::string const& pat) {
  int next[pat.size()];
  kmp_get_next(
      const_cast<char*>(pat.c_str()),
      pat.size(), next);

  return kmp_match(
      const_cast<char*>(text.c_str()), text.size(),
      const_cast<char*>(pat.c_str()), pat.size(),
      next);
}

// ========== BM Algorhtim ===============
using CharConverter = std::function<int(char)>;
int char_converter(char c) { return c; }

void bm_bc_build(char *str, int size,
                 int *bc, int bc_size,
                 CharConverter func = char_converter) {
  memset(bc, -1, bc_size * sizeof(int));
  for (int i = 0; i < size; ++i) {
    bc[func(str[i])] = i;
  }
}
void bm_gs_build(char *str, int size,
                 int *gs, int *sst = nullptr) {
  int *ss = sst ? sst : new int[size];
  maximum_suffix_match(str, size, ss);

  for (int i = 0; i < size; ++i) gs[i] = size;
  for (int i = size-1, j = 0; i >= 0; --i) {
    if (ss[i] == i + 1)
      while (j < size - 1 -i)
        gs[j++] = size - 1 - i;
  }
  for (int i = 0; i < size; ++i)
    gs[size - 1 - ss[i]] = size - 1 - i;

  if (!ss) delete[] sst;
}
int bm_match(char *text, int tsize,
             char *pat, int psize,
             int *bc, int *gs,
             CharConverter func = char_converter) {
  int i = 0, j = psize - 1;
  while (i + j < tsize) {
    while ((0 <= j) && (text[j] == pat[i+j])) j--;
    if (j < 0) break;

    int bc_next = j - bc[func(text[i+j])];
    i += (gs[j] > bc_next) ? gs[j] : bc_next;
    j = psize - 1;
  }
  return i;
}

}

#endif // CODE_STRING_H
