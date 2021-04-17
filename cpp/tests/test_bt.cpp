#include <iostream>

#include <bbcode/dsa/tree/binary_tree.h>
#include <bbcode/dsa/tree/rbt_tree.h>


using namespace bbcode;

struct ANode { };
struct BNode { int *left; };
struct CNode { void left(); };
struct DNode { int left; };

int main() {
  std::cout << "RBTNode has_left_child: "
    << has_left_child<RBTNode<int>>::value << std::endl;
  std::cout << "ANode has_left_child: "
    << has_left_child<ANode>::value << std::endl;
  std::cout << "BNode has_left_child: "
    << has_left_child<BNode>::value << std::endl;
  std::cout << "CNode has_left_child: "
    << has_left_child<CNode>::value << std::endl;
  std::cout << "DNode has_left_child: "
    << has_left_child<DNode>::value << std::endl;
}
