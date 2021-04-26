#ifndef BBCODE_OPTION_H
#define BBCODE_OPTION_H

#include <iostream>
#include <unordered_map>

#include "./types.h"

namespace bbcode {

class OptionValue {
public:
  OptionValue() : type_code(FormatType::UNKNOWN) {}

  template<typename O>
  explicit OptionValue(O const& val) 
    : type_code(FormatType::STRING) { *this = val; }

  OptionValue& operator=(std::string val) {
    // std::cout << "OPTION VALUE: " << val << "\n";
    if (type_code == FormatType::UNKNOWN)
      type_code = FormatType::STRING;

    CHECK(type_code == FormatType::STRING)
      << "uncompatiable type assignment, expected " << type2str(type_code)
      << ", but get " << type2str(FormatType::STRING);

    // copy in lazy mode, and support copy assignment by default.
    str_holder = std::make_shared<std::string>(std::move(val));
    return *this;
  }

  OptionValue& operator=(int val) {
    if (type_code == FormatType::UNKNOWN)
      type_code = FormatType::ARITHMETIC;

    CHECK(type_code == FormatType::ARITHMETIC)
      << "uncompatiable type assignment, expected " << type2str(type_code)
      << ", but get " << type2str(FormatType::ARITHMETIC);
    int_holder = val;
    return *this;
  }

  operator int() const {
    CHECK_EQ(type_code, FormatType::ARITHMETIC)
      << "invalid int type code vs. " << type2str(type_code);
    return int_holder;
  }

  operator std::string() const {
    CHECK_EQ(type_code, FormatType::STRING)
      << "invalid string type code vs. " << type2str(type_code);
    return *str_holder;
  }

  std::string to_string() const {
    std::ostringstream oss;
    switch (type_code) {
      case FormatType::ARITHMETIC: { oss << int_holder; break; }
      case FormatType::STRING: { oss << str_holder->c_str(); break; }
      default: { oss << "unknown format option"; break; }
    }
    return oss.str();
  }

private:
  int64_t int_holder;
  std::shared_ptr<std::string> str_holder;

  int type_code;
};

class Options {
public:
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

  template<typename T>
  Options& config_option(
      std::string const& name,
      int const& opt,
      T const& t) {
    std::cout << "CONFIG OPTION: " << opt << " " << t << std::endl;
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
