#include <iostream>
#include <condition_variable>
#include <thread>
#include <list>
#include <mutex>
#include <chrono>

class CTask {
public:
  CTask(int taskID) : taskID(taskID) {}

  void do_task() {
    std::cout << std::this_thread::get_id()
      << " consume a task ID is " << taskID << std::endl;
  }

private:
  int taskID;
};

std::list<std::shared_ptr<CTask>> g_task;
std::mutex g_mutex;
std::condition_variable g_conv;

void producer_func() {
  int n_taskID = 0;
  std::shared_ptr<CTask> ptask = nullptr;

  while (n_taskID < 9) {
    ptask = std::make_shared<CTask>(n_taskID);

    {
      std::lock_guard<std::mutex> lock(g_mutex);
      g_task.push_back(ptask);
      std::cout << std::this_thread::get_id()
        << " produce a task ID is " << n_taskID << std::endl;
    }

    g_conv.notify_one();

    n_taskID ++;
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
  }
}

void consumer_func() {
  std::shared_ptr<CTask> ptask = nullptr;

  int count = 0;
  while (count < 3) {
    std::unique_lock<std::mutex> lock(g_mutex);
    while (g_task.empty()) { g_conv.wait(lock); }
    ptask = g_task.front();
    g_task.pop_front();

    if (ptask == nullptr) { continue; }
    ptask->do_task();

    count ++;
  }
}

int main() {
  std::thread c1(consumer_func);
  std::thread c2(consumer_func);
  std::thread c3(consumer_func);
  // std::thread c4(consumer_func);

  std::thread p1(producer_func);
  // std::thread p2(producer_func);
  // std::thread p3(producer_func);
  // std::thread p4(producer_func);

  c1.join();
  c2.join();
  c3.join();
  // c4.join();

  p1.join();
  // p2.join();
  // p3.join();
  // p4.join();

  return 0;
}
