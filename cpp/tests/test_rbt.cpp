#include <iostream>
#include <vector>
#include <cstdio>
#include <unordered_map>
#include <cmath>

#include <bbcode/dsa/tree/rbt2_tree.h>
#include <bbcode/dsa/tree/binary_tree.h>

using namespace bbcode;

int main() {
  RBTNode<int> * root = nullptr;
  TreeRef<RBTNode<int>> ref;

  for (int i = 0; i < 20; ++i) {
    int data = std::abs((9 - i) * 7) % 39;
    root = rbt_insert(root, data);
    // ref.flatten_print(root, std::cout);
    // ref.tree(root, std::cout);
    // RBT_validate(root);
    rbt_validate<int, TreeRef>(root);
  }

  ref.print_flatten(root, std::cout);
  ref.print_ub_tree(root);
  rbt_validate<int, TreeRef>(root);

  // root = rbt_remove(root, 6);
  // root = rbt_remove(root, 35);
  auto node = rbt_find(root, 35);
  root = rbt_remove(root, node);

  ref.print_flatten(root, std::cout);
  ref.print_ub_tree(root, std::cout);
  rbt_validate<int, TreeRef>(root);
}
