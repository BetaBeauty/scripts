#ifndef LEET_CODE_H
#define LEET_CODE_H

#include "./ioutils.h"

namespace bbcode {

// =========== Reader =============

static VectorReadOption const
_default_leet_code_vector_read_option = {
  .opt = {
    .ignore = " \n",
    .comment = {"#", "//"},
    .prefix = "[",
    .suffix = "]"
  },
  .inter_suffix = ","
};

static ReadOption const
_default_leet_code_string_read_option = {
  .ignore = " \n",
  .comment = {"#", "//"},
  .prefix = "\"",
  .suffix = "\""
};

template<typename T>
class LeetCodeReader : public ReadHelper<T> {
 public:
  LeetCodeReader(std::istream & is)
    : ReadHelper<T>(is, _default_read_option) {}
};

template<>
class LeetCodeReader<std::nullptr_t>
    : public ReadHelper<std::nullptr_t> {
  typedef ReadHelper<std::nullptr_t> base_type;
 public:
  LeetCodeReader(std::istream & is)
    : base_type(is, _default_read_option)
  {}

  std::nullptr_t & read() {
    base_type::ignore();
    base_type::read(base_type::opt.prefix);
    data = nullptr;
    base_type::read(base_type::opt.suffix);
    return data;
  }
  
};

template<>
class LeetCodeReader<std::string>
    : public ReadHelper<std::string> {
  typedef ReadHelper<std::string> base_type;
 public:
  LeetCodeReader(std::istream & is)
    : ReadHelper<std::string>(is, _default_leet_code_string_read_option) {}

  std::string & read() {
    base_type::data.clear();

    base_type::ignore();
    base_type::read(base_type::opt.prefix);
    while (true) {
      if (base_type::lookup(base_type::opt.suffix)) break;
      base_type::data.push_back(base_type::is.peek());
      base_type::is.ignore(1);
    }
    base_type::read(base_type::opt.suffix);

    return data;
  }
};

template<typename T>
class LeetCodeReader<std::vector<T>>
  : public ReadHelper<std::vector<T>>,
    public LeetCodeReader<T> {
  typedef ReadHelper<std::vector<T>> base_type;
  std::string inter_suffix;
 public:
  LeetCodeReader(std::istream & is)
    : ReadHelper<std::vector<T>>(
        is, _default_leet_code_vector_read_option.opt),
      LeetCodeReader<T>(is),
      inter_suffix(_default_leet_code_vector_read_option.inter_suffix) 
    {}

 public:
  std::vector<T> & read() {
    base_type::data.clear();

    base_type::ignore();
    base_type::read(base_type::opt.prefix);
    while (true) {
      base_type::data.push_back(LeetCodeReader<T>::read());

      base_type::ignore();
      if (base_type::lookup(base_type::opt.suffix)) break;

      base_type::read(inter_suffix);
    }

    base_type::read(base_type::opt.suffix);
    return base_type::data;
  }
};

// =========== Writer =============

static VectorWriteOption const 
_default_leet_code_flatten_vector_write_option = {
  .sc = { .ident_level = 0, .prefix = "[", .suffix = "]" },
  .inter_suffix = ", "
};

static VectorWriteOption const 
_default_leet_code_vector_write_option = {
  .sc = { .ident_level = 0, .prefix = "[\n", .suffix = "\n]\n" },
  .inter_suffix = ",\n"
};

template<typename DType>
class LeetCodeWriter : public NaiveWriter<DType> {
 public:
  template<typename... Args>
  LeetCodeWriter(std::ostream & os,
                 std::string const& end="",
                 Args && ...args)
    : NaiveWriter<DType>(os, WriteOption {
        .ident_level = 0, .prefix = "", .suffix = end
      }) {
      CHECK(sizeof...(args) == 0)
        << "invalid LeetCodeWriter parameter size";
    }
};

template<typename T>
class LeetCodeWriter<std::vector<T>>
  : public LeetCodeWriter<T> {
  bool flatten;
 public:
  template<typename... Args>
  LeetCodeWriter(std::ostream & os,
                 bool flatten=false,
                 Args && ...args)
    : LeetCodeWriter<T>(os, args...),
      flatten(flatten) {}
  
  void write(std::vector<T> const& data) {
    VectorWriteOption opt = _default_leet_code_flatten_vector_write_option;
    std::string const& new_line = this->format_str() + "\n";
    opt.sc.prefix += flatten ? "" : new_line;
    opt.inter_suffix += flatten ? " " : new_line;
    opt.sc.suffix = (flatten ? "" : new_line) + opt.sc.suffix;

    int old_ident = WriteHelper::ident();
    int len = data.size();
    WriteHelper::os << WriteHelper::format_str() << opt.sc.prefix;
    for (int i = 0; i < len; ++i) {
      if (i != 0) WriteHelper::os << opt.inter_suffix;
      WriteHelper::ident() = flatten ? 0 : old_ident + 1;
      LeetCodeWriter<T>::write(data[i]);
      WriteHelper::ident() = old_ident;
    }
    this->os << opt.sc.suffix;
  }
};

// ========== Formatter ==========

struct LeetCodeIdent {
  int ident_level;
  
  LeetCodeIdent(int level = 0) : ident_level(level) {}
};

template<int Type>
struct LeetCodeFormater 
    : public LeetCodeIdent, public NaiveFormater<Type> {
  template<
    template<int> class DepFormater,
    typename T, typename... Args>
  void write(std::ostream & os, T const& data,
             std::string const& end = "",
             Args && ...args) {
    WriteOption opt {
      .ident_level = ident_level, .prefix = "", .suffix = "",
    };
    NaiveFormater<Type>::template write<DepFormater>(os, data, opt, args...);
  }
};

template<>
struct LeetCodeFormater<FormatType::ARRAY> 
    : public LeetCodeIdent {
  template<
    template<int> class DepFormater,
    typename T, typename... Args>
  void write(std::ostream & os, T const& data,
             bool flatten = true,
             Args && ...args) {
    VectorWriteOption opt = _default_leet_code_flatten_vector_write_option;
    opt.sc.ident_level = ident_level;
    if (!flatten) {
      opt.sc.prefix += "\n";
      opt.inter_suffix += "\n";
      opt.sc.suffix = "\n" + bbcode::ident_str(ident_level) + opt.sc.suffix;
    }

    os << bbcode::ident_str(opt.sc.ident_level) << opt.sc.prefix;
    DepFormater<TypeInfo<
      typename T::value_type>::value> formater;
    formater.ident_level = flatten ? 0 : ident_level + 1;
    for (auto iter = data.begin(); iter != data.end(); ++iter) {
      if (iter != data.begin()) os << opt.inter_suffix;
      formater.template write<DepFormater>(os, *iter, args...);
    }
    os << opt.sc.suffix;
  }
};

template<>
class LeetCodeFormater<FormatType::POINTER>
    : public LeetCodeIdent, public NaiveFormater<FormatType::POINTER> {
};

}

#endif // LEET_CODE_H
