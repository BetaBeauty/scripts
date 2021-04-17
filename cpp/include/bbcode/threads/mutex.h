#ifndef BBCODE_GUARD_H
#define BBCODE_GUARD_H

namespace bbcode {

/*!
 * reference: https://zhuanlan.zhihu.com/p/348492524
 */

/*!
 * try to use std::lock_guard instead of this class.
 *
 * #include <mutex>
 * std::mutex g_mutex;
 * std::local_guard<std::mutex> lock(g_mutex);
 */
template<class Mutex>
class LockGuard {
 public:
  using mutex_type = Mutex;

  explicit LockGuard(Mutex &mtx) : my_mtx_(mtx) {
    my_mtx_.lock();
  }

  ~LockGuard() noexcept { my_mtx_.unlock(); }

  LockGuard(LockGuard const&) = delete;
  LockGuard& operator=(LockGuard const&) = delete;

 private:
  Mutex &my_mtx_;
};

/*!
 * std::condition_variable
 *
 * std::condition_variable，配合std::unique_lock<std::mutex>使用，通过wait()函数阻塞线程；
 * std::condition_variable_any，可以和任意带有lock(),unlock()语义的std::mutex搭配使用,比较灵活,但是其效率不及std::condition_variable;
 *
 * std::unique_lock: C++11提供的std::unique_lock 是通用互斥包装器,允许延迟锁定,锁定的有时限尝试,递归锁定,所有权转移和与条件变量一同使用.
 * std::unique_lock比std::lock_guard使用更加灵活,功能更加强大. 
 * 使用std::unique_lock需要付出更多的时间,性能成本。
 */

} // namespace bbcode

#endif // BBCODE_GUARD_H
