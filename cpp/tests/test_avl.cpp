#include <bbcode/dsa/tree/binary_tree.h>
#include <bbcode/dsa/tree/avl_tree.h>

using namespace bbcode;

int main() {
  TreeRef<AVLNode<int>> tree;
  
  AVLNode<int> *root = nullptr;
  for (int i = 0; i < 15; ++i) {
    auto node = new AVLNode<int>();
    node->data = std::abs((9 - i) * i) % 39;
    root = avl_insert(root, node);
  }

  tree.print_flatten(root);
  tree.print_ub_tree(root);

  return 0;
}
