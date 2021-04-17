// Red and Black Tree 2

#ifndef BBCODE_RBT2_H
#define BBCODE_RBT2_H

#include <bbcode/errors.h>

namespace bbcode {

// Header API

template<typename T> struct RBTNode;

template<typename T> RBTNode<T>* rbt_insert(
    RBTNode<T> *root, RBTNode<T> *node);

// End of API


#ifndef T_LT
#define T_LT(a, b) (a < b)
#endif // T_LT

#ifndef T_EQ
#define T_EQ(a, b) (a == b)
#endif // T_EQ

#ifndef T_ASSIGN
#define T_ASSIGN(a, b) a = b
#endif // T_ASSIGN

enum Color {
  RED = 0,
  BLACK = 1,
};

template<typename T>
struct RBTNode {
  T data;
  // 0 indicates red, 1 indicates black
  Color color;
  RBTNode<T> *left, *right;
};

// Validation
template<typename T, template<typename> class TreeRef>
bool rbt_validate(RBTNode<T> *root) {
  if (root == nullptr) return true;

  CHECK(root->color == Color::BLACK) << "RBT tree root should be black";

  int height = 0;
  RBTNode<T> *cur = root;
  while (cur != nullptr) {
    if (cur->color == Color::BLACK) height ++;
    cur = cur->left;
  }

  int count = 0;
  auto visit = [height, &count](RBTNode<T> *root) {
    if (root->color == Color::RED) {
      CHECK(!root->left ||
            root->left->color != Color::RED)
        << "RBT tree has continous red nodes: "
        << serialize(root)
        << " with left child: "
        << serialize(root->left);

      CHECK(!root->right ||
            root->right->color != Color::RED)
        << "RBT tree has continous red nodes: "
        << serialize(root)
        << " with right child: "
        << serialize(root->right);
    } else {
      count ++;
    }

    if (!root->left && !root->right) {
      CHECK(count == height)
        << "Black node number is not consistent, "
        << "current height is " << count 
        << ", expected " << height;
    }
  };

  auto visited = [&count](RBTNode<T> *root) {
    if (root->color == Color::BLACK) count --;
  };

  TreeRef<RBTNode<T>> ref;
  ref.traverse(root, visit, nullptr, visited);
  return true;

}

// Data Insert

template<typename T>
RBTNode<T>* rotate_left(RBTNode<T> *root) {
  RBTNode<T> *right = root->right;

  root->right = right->left;
  right->left = root;

  return right;
}

template<typename T>
RBTNode<T>* rotate_right(RBTNode<T> *root) {
  RBTNode<T> *left = root->left;

  root->left = left->right;
  left->right = root;

  return left;
}

template<typename T>
RBTNode<T>* rbt_rebalance(RBTNode<T> *root) {
  if (root->left && root->left->color == Color::RED) {
    RBTNode<T> *left = root->left;
    if (left->left && left->left->color == Color::RED) {
      root = rotate_right(root);
      root->left->color = Color::BLACK;
    } else if (left->right &&
               left->right->color == Color::RED){
      root->left = rotate_left(root->left);
      root = rotate_right(root);
      root->left->color = Color::BLACK;
    }
  } 
  
  if (root->right && root->right->color == Color::RED) {
    RBTNode<T> *right = root->right;
    if (right->right && right->right->color == Color::RED) {
      root = rotate_left(root);
      root->right->color = Color::BLACK;
    } else if (right->left &&
               right->left->color == Color::RED) {
      root->right = rotate_right(root->right);
      root = rotate_left(root);
      root->right->color = Color::BLACK;
    }
  }

  return root;
}

template<typename T>
RBTNode<T>* rbt_insert_real(RBTNode<T> *root, RBTNode<T> *node) {
  if (root == nullptr) return node;

  if (T_LT(root->data, node->data)) {
    root->right = rbt_insert_real(root->right, node);
  } else {
    root->left = rbt_insert_real(root->left, node);
  }

  return rbt_rebalance(root);
}

template<typename T>
RBTNode<T>* rbt_insert(RBTNode<T> *root, RBTNode<T> *node) {
  node->color = Color::RED;
  root = rbt_insert_real(root, node);
  root->color = Color::BLACK;
  return root;
}

template<typename T>
RBTNode<T>* rbt_insert(RBTNode<T> *root, T data) {
  RBTNode<T> *node = new RBTNode<T>;
  node->data = data;
  return rbt_insert(root, node);
}

// Data Search

template<typename T>
RBTNode<T>* rbt_find(RBTNode<T> *root, T data) {
  while (root && !T_EQ(root->data, data)) {
    if (T_LT(root->data, data)) root = root->right;
    else root = root->left;
  }

  return root;
}

// Node Remove

template<typename T>
RBTNode<T> *rbt_replace_leaf(RBTNode<T> *node) {
  while (node->left || node->right) {
    if (node->right) {
      RBTNode<T> *succ = node->right;
      while (succ->left) succ = succ->left;
      T_ASSIGN(node->data, succ->data);
      node = succ;
    } else {
      RBTNode<T> *pred = node->left;
      while (pred->right) pred = pred->right;
      T_ASSIGN(node->data, pred->data);
      node = pred;
    }
  }
  return node;
}

template<typename T>
RBTNode<T>* rbt_rf_left_rebalance(RBTNode<T> *root, int &balanced) {
  if (balanced) return root;

  if (root->left->color == Color::RED) {
    root->left->color = Color::BLACK;
    balanced = true;
  } else if (root->right->color == Color::RED){ // must exist
    root = rotate_left(root);
    root->color = root->left->color; // must be BLACK
    root->left->color = Color::RED;
    root->left = rbt_rf_left_rebalance(root->left, balanced);
    root = rbt_rf_left_rebalance(root, balanced);
  } else if (root->right->left && root->right->left->color == Color::RED) {
    root->right = rotate_right(root->right);
    root = rotate_left(root);
    root->color = root->left->color;
    root->left->color = Color::BLACK;
    balanced = true;
  } else if (root->right->right && root->right->right->color == Color::RED) {
    root = rotate_left(root);
    root->color = root->left->color;
    root->left->color = root->right->color = Color::BLACK;
    balanced = true;
  } else {
    root->right->color = Color::RED;
  }

  return root;
}

template<typename T>
RBTNode<T>* rbt_rf_right_rebalance(RBTNode<T> *root, int &balanced) {
  if (balanced) return root;

  if (root->right->color == Color::RED) {
    root->right->color = Color::BLACK;
    balanced = true;
  } else if (root->left->color == Color::RED) { // must exist
    root = rotate_right(root);
    root->color = root->right->color;
    root->right->color = Color::RED;
    root->right = rbt_rf_right_rebalance(root->right, balanced);
    root = rbt_rf_right_rebalance(root, balanced);
  } else if (root->left->right && root->left->right->color == Color::RED) {
    root->left = rotate_left(root->left);
    root = rotate_right(root);
    root->color = root->right->color;
    root->right->color = Color::BLACK;
    balanced = true;
  } else if (root->left->left && root->left->left->color == Color::RED) {
    root = rotate_right(root);
    root->color = root->right->color;
    root->right->color = root->left->color = Color::BLACK;
    balanced = true;
  } else {
    root->left->color = Color::RED;
  }

  return root;
}

template<typename T>
RBTNode<T>* rbt_remove_real(
    RBTNode<T> *root,
    RBTNode<T> *node,
    int &balanced) {
  if (T_EQ(root->data, node->data)) { return root; }

  if (T_LT(root->data, node->data)) {
    root->right = rbt_remove_real(root->right, node, balanced);
    root = rbt_rf_right_rebalance(root, balanced);
  } else {
    root->left = rbt_remove_real(root->left, node, balanced);
    root = rbt_rf_left_rebalance(root, balanced);
  }

  return root;
}

template<typename T>
RBTNode<T>* rbt_remove_node(RBTNode<T> *root, RBTNode<T> *node) {
  if (T_EQ(root->data, node->data)) {
    delete node;
    return nullptr;
  }

  if (T_LT(root->data, node->data)) 
    root->right = rbt_remove_node(root->right, node);
  else 
    root->left = rbt_remove_node(root->left, node);

  return root;
}

template<typename T>
RBTNode<T>* rbt_remove(RBTNode<T> *root, RBTNode<T> *node) {
  // assume node is not nullptr and is in root tree
  node = rbt_replace_leaf(node);
  int balanced = false;
  root = rbt_remove_real(root, node, balanced);
  root = rbt_remove_node(root, node);
  return root;
}

template<typename T>
RBTNode<T>* rbt_remove(RBTNode<T> *root, T data) {
  RBTNode<T>* node;
  while ((node = rbt_find(root, data))) {
    root = rbt_remove(root, node);
  }
  return root;
}

}

#endif // BBCODE_RBT2_H
