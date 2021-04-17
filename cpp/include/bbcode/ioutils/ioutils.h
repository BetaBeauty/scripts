#ifndef IOUTILS_H
#define IOUTILS_H

#include <iostream>
#include <sstream>
#include <fstream>
#include <vector>
#include <cstring>
#include <algorithm>

#include <bbcode/errors.h>
#include <bbcode/templates/stl_container.h>
#include <bbcode/serializer/types.h>

namespace bbcode {

// ========= Reader =========

struct ReadOption {
  std::string ignore;
  std::vector<std::string> comment;
  std::string prefix;
  std::string suffix;
};

static ReadOption const
_default_read_option = {
  .ignore = "",
  .comment = {"#", "//"},
  .prefix = "",
  .suffix = ""
};

template<typename T>
class ReadHelper {
 protected:
  static thread_local T data;
  std::istream & is;
  ReadOption opt;

 public:
  ReadHelper(std::istream & is,
             ReadOption const& opt)
    : is(is), opt(opt) {}

  T & read() {
    ignore();
    read(opt.prefix);
    ignore();
    is >> data;
    CHECK(!is.fail()) 
      << "read index " << is.tellg()
      << " with data error " << is.peek();
    read(opt.suffix);
    return data;
  }

  void ignore() {
    while (opt.ignore.find(is.peek()) != std::string::npos)
      is.ignore(1);

    auto lookup_comment = [&]() -> bool {
      for (auto & comment : opt.comment) 
        if (lookup(comment)) return true;
      return false;
    };

    while (lookup_comment()) {
      is.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    }
  }

  void read(std::string const& str) {
    ignore();
    for (size_t i = 0; i < str.size(); ++i) {
      CHECK(is.peek() == str[i]) 
        << "invalid data format, read index " << is.tellg()
        << " with error character, expected `" << str[i]
        << "`, but got `" << (char)is.peek() << "`";
      is.ignore(1);
    }
  }

  bool lookup(std::string const& str) {
    char tmp[str.size()+1];
    int stream_pos = is.tellg();
    is.read(tmp, str.size());
    is.seekg(stream_pos);
    for (size_t i = 0; i < str.size(); ++i)
      if (tmp[i] != str[i]) return false;
    return true;
  }
};

template<typename T>
thread_local T ReadHelper<T>::data;

template<typename T>
class NaiveReader : public ReadHelper<T> {
 public:
  template<typename... Args>
  NaiveReader(std::istream & is,
              ReadOption const& opt = _default_read_option,
              Args && ...args)
    : ReadHelper<T>(is, opt) {
    CHECK(sizeof...(args) == 0)
      << "invalid parameter size in NaiveReader()";
  }
};

struct VectorReadOption {
  ReadOption opt;
  std::string inter_suffix;
};

static VectorReadOption const
_default_vector_read_option = {
  .opt = _default_read_option,
  .inter_suffix = ",",
};

template<typename T>
class NaiveReader<std::vector<T>> 
  : public ReadHelper<std::vector<T>>,
    public NaiveReader<T> {
  typedef ReadHelper<std::vector<T>> base_type;
  std::string inter_suffix;
 public:
  template<typename... Args>
  NaiveReader(std::istream & is,
              VectorReadOption const& opt = _default_vector_read_option,
              Args && ...args)
    : ReadHelper<std::vector<T>>(is, opt.opt),
      NaiveReader<T>(is, args...),
      inter_suffix(opt.inter_suffix) {}

  std::vector<T> & read() {
    base_type::data.clear();

    base_type::read(base_type::opt.prefix);
    while (true) {
      base_type::data.push_back(NaiveReader<T>::read());

      base_type::ignore();
      if (base_type::lookup(base_type::opt.suffix)) break;
      base_type::read(inter_suffix);
    }

    base_type::read(base_type::opt.suffix);
    return base_type::data;
  }
};

// ========= Writer =========

struct WriteOption {
  int ident_level;
  std::string prefix;
  std::string suffix;
};

static WriteOption const
_default_write_option = {
  .ident_level = 0,
  .prefix = "",
  .suffix = ""
};

class WriteHelper {
 protected:
  static std::string ident_str;
  std::ostream & os;
  WriteOption sc;

 public:
  WriteHelper(std::ostream & os,
              WriteOption const& sc)
    : os(os), sc(sc) {}

  int& ident() { return sc.ident_level; }
  inline std::string format_str() {
    std::ostringstream oss;
    for (int i = 0; i < sc.ident_level; ++i)
      oss << WriteHelper::ident_str;
    return oss.str();
  }

  static void SetIdentStr(std::string const& str) {
    WriteHelper::ident_str = str;
  }
};

std::string WriteHelper::ident_str = "\t";

struct VectorWriteOption {
  WriteOption sc;
  std::string inter_suffix;
};

static VectorWriteOption const
_default_vector_write_option = {
  .sc = _default_write_option,
  .inter_suffix = " "
};

template<typename T>
class NaiveWriter : public WriteHelper {
 public:
  template<typename... Args>
  NaiveWriter(std::ostream & os,
               WriteOption const& sc=_default_write_option,
               Args && ...args)
    : WriteHelper(os, sc) {
    CHECK(sizeof...(args) == 0)
      << "invalid parameter size";
  }

  void write(T const& data) {
    os << format_str() << sc.prefix
      << data << sc.suffix;
  }
};

template<>
class NaiveWriter<bool> : public WriteHelper {
 public:
  template<typename... Args>
  NaiveWriter(std::ostream & os,
               WriteOption const& sc=_default_write_option,
               Args && ...args)
    : WriteHelper(os, sc) {
    CHECK(sizeof...(args) == 0)
      << "invalid parameter size";
  }

  void write(bool data) {
    os << format_str() << sc.prefix
      << (data ? "true" : "false") << sc.suffix;
  }

};

template<typename T>
class NaiveWriter<std::vector<T>> 
    : public NaiveWriter<T> {
  VectorWriteOption vsc;
 public:
  template<typename... Args>
  NaiveWriter(std::ostream & os,
               VectorWriteOption const& vsc = _default_vector_write_option,
               Args && ...args)
    : NaiveWriter<T>(os, args...),
      vsc(vsc) { }

  void write(std::vector<T> const& data) {
    int len = data.size();
    WriteHelper::os << this->format_str() << vsc.sc.prefix;
    for (int i = 0; i < len; ++i) {
      if (i != 0) WriteHelper::os << vsc.inter_suffix;
      NaiveWriter<T>::write(data[i]);
    }
    WriteHelper::os << vsc.sc.suffix;
  }
};

template<typename T>
class NaiveWriter<T*> : public NaiveWriter<T> {
 public:
  template<typename... Args>
  NaiveWriter(std::ostream & os,
               Args && ...args)
    : NaiveWriter<T>(os, args...) {}

  void write(T* data) {
    if (data == nullptr)
      WriteHelper::os << "none";
    else
      NaiveWriter<T>::write(*data);
  }
};

template<typename T>
class NaiveWriter<std::shared_ptr<T>> : public NaiveWriter<T*> {
 public:
  template<typename... Args>
  NaiveWriter(std::ostream & os, Args && ...args)
    : NaiveWriter<T*>(os, args...) {}

  void write(std::shared_ptr<T> const& data) {
    NaiveWriter<T*>::write(data.get());
  }
    
};

// ============== Formatter =============

static std::string _single_ident = "\t";
void set_global_ident(std::string const& str) {
  _single_ident = str;
}
std::string ident_str(int ident_level) {
  std::stringstream oss;
  for (int i = 0; i < ident_level; ++i) 
    oss << _single_ident;
  return oss.str();
}

template<int Type>
struct NaiveFormater {
  template<
    template<int> class DepFormater,
    typename T, typename... Args>
  void write(std::ostream & os, T const& data,
             WriteOption const& opt = _default_write_option,
             Args && ...args) {
    ERROR() << "unknown type to format: " << TYPE_STR(T);
  }
};

template<>
struct NaiveFormater<FormatType::ARITHMETIC> {
  template<
    template<int> class DepFormater,
    typename T, typename... Args>
  void write(std::ostream & os, T const& data,
             WriteOption const& opt = _default_write_option,
             Args && ...args) {
    CHECK(sizeof...(args) == 0) << "invalid formater type";
    os << bbcode::ident_str(opt.ident_level) 
      << opt.prefix << data << opt.suffix;
  }

  template<
    template<int> class DepFormater,
    typename... Args>
  void write(std::ostream & os, bool const& data,
             WriteOption const& opt = _default_write_option,
             Args && ...args) {
    CHECK(sizeof...(args) == 0) << "invalid formater type: bool";
    os << bbcode::ident_str(opt.ident_level) 
      << opt.prefix 
      << (data ? "true" : "false")
      << opt.suffix;
  }
};

template<>
struct NaiveFormater<FormatType::ARRAY> {
  template<
    template<int> class DepFormater,
    typename T, typename... Args>
  void write(std::ostream & os, T const& data,
             VectorWriteOption const& opt = _default_vector_write_option,
             Args && ...args) {
    os << bbcode::ident_str(opt.sc.ident_level) << opt.sc.prefix;
    for (auto iter = data.begin(); iter != data.end(); ++iter) {
      if (iter != data.begin()) os << opt.inter_suffix;
      DepFormater<TYPE_VALUE(typename T::value_type)>()
        .template write<DepFormater>(os, *iter, args...);
    }
    os << opt.sc.suffix;
  }

};

template<>
struct NaiveFormater<FormatType::POINTER> {
  template<
    template<int> class DepFormater,
    typename T, typename... Args>
  void write(std::ostream & os, T const& data,
             Args && ...args) {
    if (data == nullptr) os << "nullptr";
    else {
      os << "pointer<&" << data << ">: ";
      typedef typename std::pointer_traits<T>::element_type value_type;
      DepFormater<TYPE_VALUE(value_type)>()
        .template write<DepFormater>(os, *data, args...);
    }
  }

  template<
    template<int> class DepFormater,
    typename... Args>
  void write(std::ostream & os, std::nullptr_t const&, Args && ...args) {
    os << "nullptr";
  }
};

template<template<int> class F>
class Writer {
  std::ostream & os_;
  bool new_line;

 public:
  Writer(std::ostream & os = std::cout,
         bool new_line = true) : os_(os), new_line(new_line) {}

  template<typename T, typename... Args>
  Writer& write(T const& data, Args && ...args) {
    F<TYPE_VALUE(T)>().template write<F>(os_, data, args...);
    if (new_line) os_ << "\n";
    return *this;
  }
};

}

#endif // IOUTILS_H
