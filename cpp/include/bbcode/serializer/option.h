#ifndef BBCODE_OPTION_H
#define BBCODE_OPTION_H

#include <iostream>
#include <unordered_map>

#include "./types.h"

namespace bbcode {

class OptionValue {
public:
  OptionValue() : type_code(FormatType::UNKNOWN) {}

  OptionValue(std::string const& val) { *this = val; }
  OptionValue(int val) { *this = val; }

  OptionValue& operator=(std::string const& val) {
    if (type_code == FormatType::UNKNOWN)
      type_code = FormatType::STRING;

    CHECK(type_code == FormatType::STRING)
      << "uncompatiable type assignment, expected " << type2str(type_code)
      << ", but get " << type2str(FormatType::STRING);

    // copy in lazy mode, and support copy assignment by default.
    str_holder = std::make_shared<std::string>(val);
    data.v_str = str_holder->c_str();
    return *this;
  }

  OptionValue& operator=(int val) {
    if (type_code == FormatType::UNKNOWN)
      type_code = FormatType::ARITHMETIC;

    CHECK(type_code == FormatType::ARITHMETIC)
      << "uncompatiable type assignment, expected " << type2str(type_code)
      << ", but get " << type2str(FormatType::ARITHMETIC);
    data.v_int64 = val;
    return *this;
  }

  operator int() const {
    CHECK_EQ(type_code, FormatType::ARITHMETIC)
      << "invalid int type code vs. " << type2str(type_code);
    return data.v_int64;
  }

  operator std::string() const {
    CHECK_EQ(type_code, FormatType::STRING)
      << "invalid string type code vs. " << type2str(type_code);
    return std::string(data.v_str);
  }

  std::string to_string() const {
    std::ostringstream oss;
    switch (type_code) {
      case FormatType::ARITHMETIC: { oss << data.v_int64; break; }
      case FormatType::STRING: { oss << data.v_str; break; }
      default: { oss << "unknown format option"; break; }
    }
    return oss.str();
  }

private:
  typedef union {
    int64_t v_int64;
    const char* v_str;
  } AnyType;
  AnyType data;

  std::shared_ptr<std::string> str_holder;

  int type_code;
};

class Options {
  std::unordered_map<std::string, OptionValue> opts;

public:
  template<typename O>
  Options& register_option(std::string const& name, O const& opt) {
    CHECK(opts.find(name) == opts.end())
      << "Option " << name << " has been registered";
    opts[name] = opt;
    return *this;
  }

  Options& erase_option(std::string const& name) {
    CHECK(opts.find(name) != opts.end())
      << "Option " << name << " has not been registerd";
    opts.erase(name);
    return *this;
  }

  template<typename O>
  O option(std::string const& name) const {
    auto &&it = opts.find(name);
    CHECK(it != opts.end()) << "Option: " << name << " not existed";
    return it->second;
  }

  template<typename O>
  Options& config_option(std::string const& name, O const& opt) {
    auto &&it = opts.find(name);
    CHECK(it != opts.end()) << "Option: " << name << " not existed";
    it->second = opt;
    return *this;
  }

  Options& config_option(Options const& other) {
    if (this == &other) return *this;

    for (auto &&it = other.opts.begin();
        it != other.opts.end(); ++it) {
      config_option(it->first, it->second);
    }
    return *this;
  }

  std::string to_string() const {
    std::ostringstream oss;
    for (auto it = opts.begin(); it != opts.end(); ++it) {
      oss << "<" << it->first << "=" << it->second.to_string() << ">";
    }
    return oss.str();
  }

  Options& print() {
    return const_cast<Options&>(
      static_cast<Options const&>(*this).print());
  }
  Options const& print() const {
    std::cout << to_string() << std::endl;
    return *this;
  }

};

} // namespace bbcode

#endif // BBCODE_OPTION_H
