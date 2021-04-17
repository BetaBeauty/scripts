#ifndef BBCODE_SUGAR_H
#define BBCODE_SUGAR_H

#include <memory>
#include <functional>

#include <bbcode/macro.h>

namespace bbcode {

using DeferFuncType = std::function<void()>;

class DeferredAction {
  DeferFuncType *_func;
  bool _cancelled = false;

 public:
  DeferredAction(DeferFuncType &func) : _func(&func) {}
  // DeferredAction(Func &&func) : _func(std::move(func)) {}
  ~DeferredAction() { 
    if(!_cancelled) (*_func)();
  }

  void cancel() { _cancelled = true; }
};

/**
 * Support two kinds of defer macros:
 *  1. DEFER_FUNC will hold a defer_handler named `Handler`,
 *    one can cancel the defer function manually via invoking
 *    `Handler.cancel()` funtion.
 *  2. AUTO_DEFER will auto execute the defer function defined
 *    by user, and user cannot cancel it.
 **/

#define DEFER_FUNC(Handler) \
  bbcode::DeferFuncType CONCAT(defer_func_, __LINE__); \
  bbcode::DeferredAction Handler( CONCAT(defer_func_, __LINE__) ); \
  CONCAT(defer_func_, __LINE__) = [&]()

#define AUTO_DEFER() DEFER_FUNC(CONCAT(defer_handler_, __LINE__))
}

#endif // BBCODE_SUGAR_H
