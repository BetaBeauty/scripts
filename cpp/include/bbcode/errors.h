#ifndef CODE_ERRORS_H
#define CODE_ERRORS_H

#include <sstream>
#include <exception>
#include <stdexcept>
#include <vector>
#include <memory>

#include <execinfo.h>
#include <cxxabi.h>

namespace bbcode {

#define ERROR() \
  bbcode::details::LogFatal(__FILE__, __LINE__).stream()

#define CHECK(cond) \
  if (!(cond)) ERROR() << " Check Failed: [" #cond << "] "

#define CHECK_BIN_OP(a, b, op) \
  CHECK(a op b) << a << " vs. " << b << " "
#define CHECK_EQ(a, b) CHECK_BIN_OP(a, b, ==)

namespace details {

inline std::string Demangle(void *trace, char const *msg_str) {
  using std::string;
  string msg(msg_str);
  size_t symbol_start = string::npos;
  size_t symbol_end = string::npos;
  if ( ((symbol_start = msg.find("_Z")) != string::npos)
             && (symbol_end = msg.find_first_of(" +", symbol_start)) ) {
      string left_of_symbol(msg, 0, symbol_start);
      string symbol(msg, symbol_start, symbol_end - symbol_start);
      string right_of_symbol(msg, symbol_end);
  
      int status = 0;
      size_t length = string::npos;
      std::unique_ptr<char, decltype(&std::free)> demangled_symbol =
              {abi::__cxa_demangle(symbol.c_str(), 0, &length, &status), &std::free};
      if (demangled_symbol && status == 0 && length > 0) {
            string symbol_str(demangled_symbol.get());
            std::ostringstream os;
            os << left_of_symbol << symbol_str << right_of_symbol;
            return os.str();
          }
    }
  return string(msg_str);
}

inline std::string StackTrace(const size_t stack_size = 10) {
  using std::string;
  std::ostringstream stacktrace_os;
  std::vector<void*> stack(stack_size);
  int nframes = backtrace(stack.data(), static_cast<int>(stack_size));
  stacktrace_os << "Stack trace returned " << nframes << " entries:" << std::endl;
  char **msgs = backtrace_symbols(stack.data(), nframes);
  if (msgs != nullptr) {
      for (int frameno = 0; frameno < nframes; ++frameno) {
            string msg = Demangle(stack[frameno], msgs[frameno]);
            stacktrace_os << "[bt] (" << frameno << ") " << msg << "\n";
          }
    }
  free(msgs);
  string stack_trace = stacktrace_os.str();
  return stack_trace;
}

class LogFatal {
  std::ostringstream log_;
 public:
  LogFatal(char const * file, int line) {
    log_ << "\n\n>>> Error at " << file << ":" << line << "\n"
      << StackTrace() << "\n";
  }

  std::ostringstream & stream() { return log_; }

  ~LogFatal() noexcept(false) {
    throw std::runtime_error(log_.str() + "\n");
  }

};

} // namespace details

} // namespace bbcode

#endif // CODE_ERRORS_H
