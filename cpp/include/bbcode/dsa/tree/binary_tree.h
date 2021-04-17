#ifndef CODE_BINARY_TREE_H
#define CODE_BINARY_TREE_H

#include <functional>
#include <unordered_map>
#include <iostream>

#include <bbcode/errors.h>
#include <bbcode/serializer/serializer.h>
#include <bbcode/templates/template_utils.h>

namespace bbcode {

template<typename T>
class has_left_child {
  template<typename U, typename C>
  static details::Type1& test(decltype( static_cast<T*>(U::left)) );

  template<typename U, typename C> static details::Type2& test(...);

 public:
  static const bool value = 
    sizeof(test<T, T*>(nullptr)) == sizeof(details::Type1);
};

template<typename T>
class has_right_child {
  template<typename U, typename C>
  static details::Type1& test(decltype( static_cast<T*>(U::right)) );

  template<typename U, typename C> static details::Type2& test(...);

 public:
  static const bool value = 
    sizeof(test<T, T*>(nullptr)) == sizeof(details::Type1);
};

template<typename T>
class is_bt
  : public std::integral_constant<bool,
    has_left_child<T>::value &&
    has_right_child<T>::value>
{};

template<typename T>
using VisitFunc = std::function<void(T *)>;

template<typename T>
class TreeRef {
 public:
  TreeRef() {
    CHECK(has_left_child<T>::value)
      << "The reference node must have pointer to self "
      << "named `left`.";
    CHECK(has_right_child<T>::value)
      << "The reference node must have pointer to self "
      << "named `right`.";
  }

  virtual void traverse(
      T *node,
      VisitFunc<T> pre_order = nullptr,
      VisitFunc<T> mid_order = nullptr,
      VisitFunc<T> suf_order = nullptr) {
    if (node == nullptr) return ;

    if (pre_order) pre_order(node);
    if (node->left)
      traverse(node->left, pre_order, mid_order, suf_order);
    if (mid_order) mid_order(node);
    if (node->right)
      traverse(node->right, pre_order, mid_order, suf_order);
    if (suf_order) suf_order(node);
  }

  virtual void print_flatten(
      T *root, std::ostream &os = std::cout) {
    auto _print = [&](T *root) {
      os << serialize(root) << " ";
    };

    traverse(root, nullptr, _print);
    os << "\n";
  }

  virtual void print_ub_tree(T *root, std::ostream &os = std::cout) {
    std::unordered_map<T*, int> map_lens;
    std::unordered_map<T*, int> map_locs;
    std::unordered_map<T*, int> map_offsets;

    auto _get = [&](T *node) {
      if (node == nullptr) return ;

      int len = serialize(node).size();

      map_lens[node] = len + map_lens[node->left] +
        map_lens[node->right];
      map_offsets[node] = map_lens[node->left] + len / 2;
      map_locs[node->left] = 0;
      map_locs[node->right] = map_lens[node->left] + len;
    };

    traverse(root, nullptr, nullptr, _get);

    std::vector<std::string> strs;
    int layer = 0;
    auto _print = [&](T *node) {
      if (layer + 1 > (int)strs.size()) strs.resize(layer + 1);

      int start = map_locs[node], len = map_lens[node];
      strs[layer].resize(start, ' ');
      strs[layer].resize(start+len, ' ');
      if (node->left) {
        std::string s(
          map_lens[node->left] - map_offsets[node->left],
          '-');
        s[0] = ',';
        strs[layer].replace(
          start + map_offsets[node->left],
          s.size(), s);
      }

      std::string int_str = serialize(node);
      strs[layer].replace(
        start + map_lens[node->left],
        int_str.size(), int_str);

      if (node->right) {
        std::string s(map_offsets[node->right], '-');
        s += ',';
        strs[layer].replace(
          start + map_lens[node->left] + int_str.size(),
          s.size(), s);
      }

      map_locs[node->left] = start;
      map_locs[node->right] = start + 
        map_lens[node->left] + int_str.size();

      layer ++;
    };

    auto _release = [&](T *node) { layer --; };

    traverse(root, _print, nullptr, _release);

    if (strs.size() == 0) os << "NONE\n";
    for (auto str : strs) {
      os << str << "\n";
    }
    os << "\n";
  }
};

}

#endif // CODE_BINARY_TREE_H
