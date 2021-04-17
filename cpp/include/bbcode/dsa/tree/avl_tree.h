#ifndef BBCODE_AVL_H
#define BBCODE_AVL_H

namespace bbcode {

// Header API

template<typename T> struct AVLNode;

template<typename T> AVLNode<T>* avl_insert(
    AVLNode<T> *root, AVLNode<T> *node);

// End of API


#ifndef T_LT
#define T_LT(a, b) a < b
#endif

template<typename T>
struct AVLNode {
  T data;
  int height;
  AVLNode *left, *right;
};

#define TREE_HEIGHT(X) (X ? X->height : -1)

template<typename T>
int get_balance_factor(AVLNode<T> *node) {
  if (node == nullptr) return 0;
  return TREE_HEIGHT(node->left) - TREE_HEIGHT(node->right);
}

template<typename T>
void update_height(AVLNode<T>* root) {
  int lh = TREE_HEIGHT(root->left);
  int rh = TREE_HEIGHT(root->right);
  root->height = 1 + (lh > rh ? lh : rh);
}

// NOTICE: Rotate left & right is not responsible for
//  the corrent height of sub-tree root. The quick return
//  branch can be triggered in the rebalance function.
template<typename T>
AVLNode<T>* rotate_right(AVLNode<T> *root) {
  AVLNode<T> *left = root->left;

  root->left = left->right;
  left->right = root;

  update_height(root);
  return left;
}

template<typename T>
AVLNode<T>* rotate_left(AVLNode<T> *root) {
  AVLNode<T> *right = root->right;

  root->right = right->left;
  right->left = root;

  update_height(root);
  return right;
}

template<typename T>
AVLNode<T>* avl_rebalance(AVLNode<T> *root) {
  int factor = get_balance_factor(root);
  if (factor > 1) {
    if (get_balance_factor(root->left) < 0) {
      root->left = rotate_left(root->left);
      update_height(root->left); // update height manually
    }
    root = rotate_right(root);
  } else if (factor < -1){
    if (get_balance_factor(root->right) > 0) {
      root->right = rotate_right(root->right);
      update_height(root->right); // update height manually

    }
    root = rotate_left(root);
  }

  update_height(root);
  return root;
}

template<typename T>
AVLNode<T>* avl_insert(AVLNode<T> *root, AVLNode<T> *node) {
  if (root == nullptr) {
    update_height(node);
    return node;
  }

  if (T_LT(root->data, node->data)) {
    root->right = avl_insert(root->right, node);
  } else {
    root->left = avl_insert(root->left, node);
  }

  return avl_rebalance(root);
}

} // namespace bbcode

#endif // BBCODE_AVL_H
