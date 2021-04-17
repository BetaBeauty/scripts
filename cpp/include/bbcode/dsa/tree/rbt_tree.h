// Red and Black Tree

#ifndef CODE_RBT_H
#define CODE_RBT_H

#include <functional>

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

#define RB_RED 0
#define RB_BLACK 1

template<typename T>
struct RBTNode {
  T data;
  // 0 indicates red, 1 indicates black
  int type; 
  RBTNode<T> *left, *right, *parent;
};

template<typename T>
RBTNode<T>* RBT_node(T data, int type = RB_RED) {
  return new RBTNode<T> {
    data, type, // initialize new node as red color.
    nullptr, nullptr, nullptr
  };
}

// Red and Black Tree Validation
template<typename T, template<typename> class TreeRef>
bool rbt_validate(RBTNode<T> *root) {
  if (root == nullptr) return true;

  CHECK_EQ(root->type, RB_BLACK) << "RBT tree root should be black";

  int height = 0;
  RBTNode<T> *cur = root;
  while (cur != nullptr) {
    if (cur->type == RB_BLACK) height ++;
    cur = cur->left;
  }

  int count = 0;
  auto visit = [height, &count](RBTNode<T> *root) {
    if (root->type == RB_RED) {
      CHECK(root->parent->type != RB_RED)
        << "RBT tree has continous red node";
    } else {
      count ++;
    }

    if (root->left == nullptr && root->right == nullptr) {
      CHECK_EQ(count, height)
        << "black node number is not consistent, "
        << "current height is " << count 
        << ", expected " << height;
    }
  };

  auto visited = [&count](RBTNode<T> *root) {
    if (root->type == RB_BLACK) count --;
  };

  TreeRef<RBTNode<T>> ref;
  ref.traverse(root, visit, nullptr, visited);
  return true;
}

template<typename T>
RBTNode<T>* rbt_find(T data, RBTNode<T> *root) {
  if (root == nullptr) return nullptr;

  RBTNode<T> *ptr = root;
  while (!T_EQ(data, ptr->data)) {
    RBTNode<T> *trival = nullptr;
    if (T_LT(data, ptr->data)) trival = ptr->left;
    else trival = ptr->right;

    if (trival == nullptr) break;
    ptr = trival;
  }

  return ptr;
}

// connect the relationship between child and parent
// P must not be nullptr
#define RBT_BIND_L(C, P) \
  { if (C) C->parent = P; if (P) P->left = C; }
#define RBT_BIND_R(C, P) \
  { if (C) C->parent = P; if (P) P->right = C; }

#define RBT_IS_LEFT_CHILD(C, P) \
  (P && P->left && T_EQ(P->left->data, C->data))

template<typename T>
void RBT_left_roll(RBTNode<T> *C) {
  RBTNode<T> *P = C->parent;
  RBTNode<T> *R = C->right;
  RBTNode<T> *RL = R->left;

  if (RBT_IS_LEFT_CHILD(C, P)) {
    RBT_BIND_L(R, P);
  } else {
    RBT_BIND_R(R, P);
  }
  RBT_BIND_L(C, R);
  RBT_BIND_R(RL, C);
}

template<typename T>
void RBT_right_roll(RBTNode<T> *C) {
  RBTNode<T> *P = C->parent;
  RBTNode<T> *L = C->left;
  RBTNode<T> *LR = L->right;
  
  if (RBT_IS_LEFT_CHILD(C, P)) {
    RBT_BIND_L(L, P);
  } else {
    RBT_BIND_R(L, P);
  }
  RBT_BIND_R(C, L);
  RBT_BIND_L(LR, C);
}

/**
 * RBT Tree Bottom-Up Self Balance
 *
 * 1. Initialize with injected RED node.
 *
 * 2. Suppose the tree height keep the same for each updated
 *  node in recursive invokation for self balance.
 *
 * 3. Suppose the current node is always RED color.
 *
 **/
template<typename T>
RBTNode<T>* RBT_balance(RBTNode<T> *C, RBTNode<T> *root) {
  // case 1 : the current node is root, mark as black,
  //  which will increase the height of tree and it's
  //  the only situation to change tree height.
  if (C->parent == nullptr) {
    C->type = RB_BLACK;
    return C;
  }

  RBTNode<T> *P = C->parent;
  RBTNode<T> *PP = P->parent;

  // case 2 : the parent node is black, insert directly
  if (P->type == RB_BLACK) return root;

  // case 3 : the parent node is red
  /**
   * The parent node is red, which means the grandparent
   *  node is existed whose color is black since the root is 
   *  always black and there mustn't be two continous red
   *  nodes.
   **/
  if (RBT_IS_LEFT_CHILD(C, P)) {
    if (RBT_IS_LEFT_CHILD(P, PP)) {
      RBT_right_roll(PP);
      C->type = RB_BLACK;
      root = RBT_balance(P, root);
    } else {
      RBT_right_roll(P);
      RBT_left_roll(PP);
      P->type = RB_BLACK;
      root = RBT_balance(C, root);
    }
  } else {
    if (RBT_IS_LEFT_CHILD(P, PP)) {
      RBT_left_roll(P);
      RBT_right_roll(PP);
      P->type = RB_BLACK;
      root = RBT_balance(C, root);
    } else {
      RBT_left_roll(PP);
      C->type = RB_BLACK;
      root = RBT_balance(P, root);
    }
  }

  return root;
}

// insert node into root tree, returns new root tree.
template<typename T>
void rbt_insert(T data, RBTNode<T> *& root) {
  // if tree is empty, return new tree and mark as black.
  if (root == nullptr) {
    root = RBT_node(data, RB_BLACK);
    return ;
  }

  RBTNode<T> *P = rbt_find(data, root);
  // if the node has existed in tree, do nothing.
  if (T_EQ(data, P->data)) { return ; }

  RBTNode<T> *C = RBT_node(data);
  if (T_LT(data, P->data)) { RBT_BIND_L(C, P); }
  else { RBT_BIND_R(C, P); }

  root = RBT_balance(C, root);
}

template<typename T>
RBTNode<T> * RBT_remove_node(RBTNode<T> *C, RBTNode<T> *root) {
  RBTNode<T> *P = C->parent;
  if (P == nullptr) return nullptr;

  if (RBT_IS_LEFT_CHILD(C, P)) {
    P->left = nullptr;
  } else if (P) {
    P->right = nullptr;
  }

  delete C;
  return root;
}

template<typename T>
void RBT_remove_balance(RBTNode<T> *C) {
  // if the current node is red, set as black.
  if (C->type == RB_RED) { 
    C->type = RB_BLACK;
    return ; 
  } 

  // if the current node is root, do nothing
  // and the total tree height will decrease one.
  if (C->parent == nullptr) { return ; }

  RBTNode<T> *P = C->parent;
  if (RBT_IS_LEFT_CHILD(C, P)) {
    RBTNode<T> *R = P->right;
    if (R->type == RB_RED) { 
      // TODO
      RBT_left_roll(P);
      P->type = RB_RED;
      R->type = RB_BLACK;
      RBT_remove_balance(C);
    } else {
      RBTNode<T> *RL = R->left;
      RBTNode<T> *RR = R->right;

      if (RL && (RL->type == RB_RED)) {
        RBT_right_roll(R);
        RBT_left_roll(P);
        RL->type = P->type;
        P->type = RB_BLACK;
      } else if (RR && (RR->type == RB_RED)) {
        RBT_left_roll(P);
        R->type = P->type;
        P->type = RB_BLACK;
        RR->type = RB_BLACK;
      } else {
        // if P is RED, will return at the front of function.
        R->type = RB_RED;
        RBT_remove_balance(P);
      }
    }
  } else {
    RBTNode<T> *L = P->left;
    if (L->type == RB_RED) {
      RBT_right_roll(P);
      P->type = RB_RED;
      L->type = RB_BLACK;
      RBT_remove_balance(C);
    } else {
      RBTNode<T> *LL = L->left;
      RBTNode<T> *LR = L->right;

      if (LR && (LR->type == RB_RED)) {
        RBT_left_roll(L);
        RBT_right_roll(P);
        LR->type = P->type;
        P->type = RB_BLACK;
      } else if (LL && (LL->type == RB_RED)) {
        RBT_right_roll(P);
        L->type = P->type;
        P->type = RB_BLACK;
        LL->type = RB_BLACK;
      } else {
        // if P is RED, will return at the front of function.
        L->type = RB_RED;
        RBT_remove_balance(P);
      }
    }
  }
}

template<typename T>
bool RBT_remove(T data, RBTNode<T>* & root) {
  RBTNode<T> *C = rbt_find(data, root);
  if (C == nullptr) return false;
  if (C->data != data) return false;

  while (C->left != nullptr || C->right != nullptr) {
    if (C->left == nullptr) { 
      C->data = C->right->data;
      RBT_BIND_L(C->right->left, C);
      C->right->left = nullptr;
      C = C->right; 
    } else if (C->right == nullptr) { 
      C->data = C->left->data;
      RBT_BIND_R(C->left->right, C);
      C->left->right = nullptr;
      C = C->left; 
    } else {
      RBTNode<T> *succ = C->right;
      while (succ->left) { succ = succ->left; }
      C->data = succ->data;
      C = succ;
    }
  }

  RBT_remove_balance(C);
  root = RBT_remove_node(C, root);
  return true;
}

}

#endif // CODE_RBT_H
